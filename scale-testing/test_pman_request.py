#!/usr/bin/env python3

import os, sys
sys.path.append(os.path.abspath('../'))
from test_request import test_request
import configparser
import matplotlib.pyplot as plt
import numpy as np
from subprocess import Popen, PIPE
import uuid
import shlex
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

config = configparser.ConfigParser()
config.read('config.cfg')

CAPTURE = config.get('ConfigInfo', 'CAPTURE')
RANGE = int(config.get('ConfigInfo', 'RANGE'))
PID = config.get('ConfigInfo', 'PID')
PMAN_IP = config.get('ConfigInfo', 'PMAN_IP')
PFIOH_IP = config.get('ConfigInfo', 'PFIOH_IP')
PLUGIN = config.get('ConfigInfo', 'PLUGIN')
PATH = config.get('ConfigInfo', 'CHRIS_PATH')
SIZE = config.get('ConfigInfo', 'SIZE')

dt = datetime.datetime.now()
r_name = "test_pman_request_results_%s_%s.txt" % (str(dt.date()), str(dt.time()))
results = open(r_name, "x")
results.write("METRICS: %s concurrent requests of size %s\n" % (str(RANGE), str(SIZE)))

if CAPTURE:
    # get PID of pman
    process = Popen("pgrep pman", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    PID = int(stdout)
else:
    PID = 0

# Make x concurrent requests to pman and capture and log resource utilization 
for x in range(1, RANGE + 1):
    print("Iteration " + str(x))
    print("_________________")

    pman_req = test_request(PID, 'pman', CAPTURE)

    # add all threads 
    for n in range(1, x + 1):
        new_id = (str(uuid.uuid4())).split('-')
        JID = new_id[-1]
        #JID = uuid.uuid4()

        # push to 
        cmd = 'bash %s/ChRIS-E2E/scripts/run_pfioh_push %s %s /tmp/%s' % (PATH, PFIOH_IP, JID, SIZE)
        process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
        stdout, stderr = process.communicate()

        #cmd = 'bash pman_scale/pman.sh %s run %s %s' % (str(JID), IP, PLUGIN)
        cmd = 'bash %s/ChRIS-E2E/scripts/run_pman %s %s %s' % (PATH, str(JID), PMAN_IP, PLUGIN)
        pman_req.add(cmd, JID, PMAN_IP)        
    pman_req.start()

    # Append results of each iteration to their respective lists
    pman_req.join()
    s_rate.append(int(pman_req.get_success()))
    nums.append(x)

    if CAPTURE:
        cpu.append(pman_req.get_cpu_util())
        mem.append(pman_req.get_mem_util())

    dur.append(pman_req.get_runtime())
    throughput = x / pman_req.get_runtime()
    thr.append(throughput)

avg_runtime = 0
avg_throughput = 0
avg_mem = 0
avg_cpu = 0
avg_success = 0

for z in range(x):
    avg_runtime += dur[z]
    avg_throughput += thr[z]
    avg_mem += mem[z]
    avg_cpu += cpu[z]
    avg_success += s_rate[z]

avg_runtime = avg_runtime/x
avg_throughput = avg_throughput/x
avg_mem = avg_mem/x
avg_cpu = avg_cpu/x
avg_success = avg_success/x

results.write("Average Runtime: %s\n" % str(avg_runtime))
results.write("Average Throughput: %s\n" % str(avg_throughput))
results.write("Average Memory Utilization: %s\n" % str(avg_mem))
results.write("Average CPU Utilization: %s\n" % str(avg_cpu))
results.write("Average Success Rate: %s\n" % str(avg_success))
results.close()
    
################## Graph results ####################    

#c_range = config['RANGE']
fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

if CAPTURE:
    ax0.plot(nums, cpu)
    ax1.plot(nums, mem)
    
ax0.bar(np.arange(RANGE), s_rate, color='r')
ax2.plot(nums, dur)
ax3.plot(nums, thr)

if CAPTURE:
    ax0.set_title('CPU Utilization')
    ax1.set_title('Memory Utilization')
else:
    ax0.set_title('Success rate')
    
ax2.set_title('Duration')
ax3.set_title('Throughput')

if CAPTURE:
    ax0.axis([0, RANGE, 0, 200])
    ax1.axis([0, RANGE, 0, 10])

ax2.axis([0, RANGE, 0, 10])
ax3.axis([0, RANGE, 0, 25])

plt.show()
