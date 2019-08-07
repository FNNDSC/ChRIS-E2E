#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath('pman_scale/'))
sys.path.append(os.path.abspath('pfioh_scale/'))

from test_request import test_request
import test_setup
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from subprocess import Popen, PIPE
import uuid
import math
import shlex
import time
import configparser
import string
import json
import datetime

"""
Performs scalability and performance tests by making increasingly more concurrent requests to pman and capturing resource utilization                         
"""

nums = []                                 # Number of concurrent requests being made to pman
cpu = []                                  # CPU utilization
mem = []                                  # Memory utilization
thr = []                                  # Throughput
dur = []                                  # Duration
s_rate = []                               # Success rate

PID = 0

dirs = []
index = 0

config = configparser.ConfigParser()
config.read('config.cfg')

# Creates test directories if they don't already exist
test_setup.check()
test_setup.clean()

RANGE = (int)(config.get('ConfigInfo', 'RANGE'))
CAPTURE = config.get('ConfigInfo', 'CAPTURE')
PFIOH_IP = config.get('ConfigInfo', 'PFIOH_IP')
SIZE = config.get('ConfigInfo', 'SIZE')
PATH = config.get('ConfigInfo', 'CHRIS_PATH')
IMAGE = config.get('ConfigInfo', 'PLUGIN')
PMAN_IP = config.get('ConfigInfo', 'PMAN_IP')
PMAN_CMD = config.get('ConfigInfo', 'CMD')
MAX_DELAY = (int)(config.get('ConfigInfo', 'MAX_DELAY'))

# Create file to hold output

dt = datetime.datetime.now()
r_name = "test_local_results_%s_%s.txt" % (str(dt.date()), str(dt.time()))
results = open(r_name, "x")
results.write("METRICS: %s concurrent requests of size %s\n" % (str(RANGE), str(SIZE)))


print ("Running test_local...\n")

################ PFIOH PUSH ########################

# Clear log                                                                                  
subprocess.call('> /tmp/top.log', shell=True)

# Start measuring here        
if CAPTURE:     
     process = Popen("pgrep pfioh", stdout=PIPE, stderr=PIPE, shell=True)
     stdout, stderr = process.communicate()
     PID = int(stdout)
     subprocess.call(["top -p " + str(PID) + " -d 0.2 -b | grep --line-buffered pfioh | awk '{print $9, $10}' >> /tmp/top.log &"], shell=True)
     #time.sleep(2)
     start = time.time()

# run pfioh
pfioh_success = 0

print ("Pushing to " + PFIOH_IP + "...\n")

for x in range(RANGE):
     push_file = 'tmp/share/%s' % SIZE
     new_id = (str(uuid.uuid4())).split('-')
     jid = new_id[-1]
     dirs.append(jid)
     cmd = 'bash %s/ChRIS-E2E/scripts/run_pfioh_push %s %s /tmp/%s' % (PATH, PFIOH_IP, jid, SIZE)
     print(cmd)
     process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
     stdout, stderr = process.communicate()

     try:
          response = json.loads(stdout)
          print(response['stdout']['msg'])
          if response['stdout']['status']:
               pfioh_success += 1
     except (ValueError, TypeError):
          print ("Error: problem loading response as JSON\n")
          print (stdout)
     
     
# compute cpu and memory utilization, runtime, and success rate
if CAPTURE:
     subprocess.call("kill -9 $(pgrep top)", shell=True)

     time.sleep(2)
     
     runtime = time.time() - start
     count = 0
     cpu = []
     mem = 0

     f = open("/tmp/top.log", "r")
     for line in f:
          try:
               curr = line.split()
               cpu.append(float(curr[0]))
               mem += float(curr[1])
               count += 1
          except IndexError:
               continue

     f.close()
     print ("\n")

     cpu_util = max(cpu)
     mem_util = mem/count

     success = (pfioh_success / RANGE) * 100 
     pfioh_results = "PFIOH PUSH: \n____________\nCPU utilization is: %s\nMemory utilization is: %s\nRuntime is %s\nSuccess rate is: %s\n\n" % (str(cpu_util), str(mem_util), str(runtime), str(success))

     print(pfioh_results)
     results.write(pfioh_results)

     """
     print ("PFIOH PUSH: \n")
     print ("____________\n")
     print ("CPU utilization is: " + str(cpu_util))
     print ("Memory utilization is: " + str(mem_util))
     print ("Runtime is " + str(runtime))
     print ("Success rate is: " + str(success) + "%\n\n")
     """

###################### PMAN ############################

pman_success = 0

# Clear log
subprocess.call('> /tmp/top.log', shell=True)

# Start measuring here
if CAPTURE:
     process = Popen("pgrep pman", stdout=PIPE, stderr=PIPE, shell=True)
     stdout, stderr = process.communicate()
     PID = int(stdout)
     subprocess.call(["top -p " + str(PID) + " -d 0.2 -b | grep --line-buffered pman | awk '{print $9, $10}' >> /tmp/top.log &"], shell=True)
     time.sleep(2)
     start = time.time()

print ("Executing pman requests...\n")
     
for z in dirs:
     cmd = 'bash %s/ChRIS-E2E/scripts/run_pman %s %s %s' % (PATH, z, PMAN_IP, IMAGE)
     process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
     stdout, stderr = process.communicate()

     print(stdout)
     print(stderr)
     
     response = json.loads(stdout)
     
     print(response)
     
incomplete = dirs.copy()

status_count = 1
wait_time = 0

# while there are jobs in progress and overall wait time has not exceeded the max_delay set in config.cfg
while (incomplete != [] and wait_time <= MAX_DELAY):

     for job in incomplete:
          cmd = 'bash %s/ChRIS-E2E/scripts/run_pman_status %s %s' % (PATH, PMAN_IP, job)
          process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
          stdout, stderr = process.communicate()

          try:
               response = json.loads(stdout)
               if (((response['d_ret']['l_status'])[0]) == "finished"):
                    incomplete.remove(job)
                    pman_success += 1
                    print("Job " + str(job) + " succeeeded!")
               elif (((response['d_ret']['l_status'])[0]) == "started"):
                    print("Job " + str(job) + " in progress")
               else:
                    print("Job " + str(job) + " failed or incomplete")
          except (ValueError, TypeError):
               print ("Error: problem loading response as JSON\n")
               print (stdout)

          # time.sleep as a function of status_count so you don't overwhelm the system with status requests as time goes on
          time.sleep(2 * math.log(status_count))

          wait_time += (2 * math.log(status_count))
          status_count += 1
          
if CAPTURE:
     subprocess.call("kill -9 $(pgrep top)", shell=True)

     runtime = time.time() - start
     count = 0
     cpu = []
     mem = 0

     f = open("/tmp/top.log", "r")
     for line in f:
          try:
               curr = line.split()
               cpu.append(float(curr[0]))
               mem += float(curr[1])
               count += 1
          except IndexError:
               continue
          
     f.close()
     print ("\n")

     cpu_util = max(cpu)
     mem_util = mem/count
     success_rate = (pman_success/len(dirs)) * 100

     pman_results = "PMAN: \n____________\nCPU utilization is: %s\nMemory utilization is: %s\nRuntime is %s\nSuccess rate is: %s\n\n" % (str(cpu_util), str(mem_util), str(runtime), str(success))

     print(pman_results)
     results.write(pman_results)
     
     """
     print ("PMAN:\n")
     print ("____________\n")
     print ("CPU utilization is: " + str(cpu_util))
     print ("Memory utilization is: " + str(mem_util))
     print ("Runtime is " + str(runtime))
     print ("Success rate is: " + str(success_rate) + "%\n\n")
     """

     
####################### PFIOH PULL ######################

# Clear log                                                                                                                                   

subprocess.call('> /tmp/top.log', shell=True)

# Start measuring here                                                                                                                        

if CAPTURE:
     process = Popen("pgrep pfioh", stdout=PIPE, stderr=PIPE, shell=True)
     stdout, stderr = process.communicate()
     PID = int(stdout)
     subprocess.call(["top -p " + str(PID) + " -d 0.2 -b | grep --line-buffered pfioh | awk '{print $9, $10}' >> /tmp/top.log &"], shell=True)
     time.sleep(2)
     start = time.time()

pfioh_success = 0

print ("Pulling from " + PFIOH_IP + "...\n")

for y in dirs:
     push_dir = 'pushto/%s' % y
     cmd = 'sudo bash %s/ChRIS-E2E/scripts/run_pfioh_pull %s %s %s' % (PATH, PFIOH_IP, y, push_dir)
     process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
     stdout, stderr = process.communicate()

     try:
          response = json.loads(stdout)
          print(response['stdout']['msg'])
          if response['stdout']['status']:
               pfioh_success += 1
     except (ValueError, TypeError):
          print ("Error: problem loading response as JSON\n")
          print (stdout)

if CAPTURE:
     subprocess.call("kill -9 $(pgrep top)", shell=True)

     time.sleep(2)
     
     runtime = time.time() - start
     count = 0
     cpu = []
     mem = 0

     f = open("/tmp/top.log", "r")
     for line in f:
          try:
               curr = line.split()
               cpu.append(float(curr[0]))
               mem += float(curr[1])
               count += 1
          except IndexError:
               continue

     f.close()
     print ("\n")

     cpu_util = max(cpu)
     mem_util = mem/count
     success_rate = (pfioh_success / RANGE) * 100

     pfioh_results = "PFIOH PULL: \n____________\nCPU utilization is: %s\nMemory utilization is: %s\nRuntime is %s\nSuccess rate is: %s\n\n" % (str(cpu_util), str(mem_util), str(runtime), str(success))

     print(pfioh_results)
     results.write(pfioh_results)
     results.close()
     
     """
     print ("PFIOH PULL:\n")
     print ("____________\n")
     print ("CPU utilization is: " + str(cpu_util))
     print ("Memory utilization is: " + str(mem_util))
     print ("Runtime is " + str(runtime) + "\n\n")
     print ("Success rate is: " + str(success) + "%\n")
     """

