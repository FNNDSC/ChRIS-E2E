#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath('../'))
from test_request import test_request
#from scale_threads import scale_threads
#import time
#import threading
import matplotlib.pyplot as plt
import numpy as np
from subprocess import Popen, PIPE
import test_setup
import uuid
import configparser
#import config as cfg 
import datetime

"""
Performs scalability and performance tests by making increasingly more concurrent push/pull requests to pfioh and measuring resultant resource utilization and success rate
"""

nums = []                                  # Number of concurrent requests being made to pfioh
cpu = []                                   # CPU utilization
mem = []                                   # Memory utilization
thr = []                                   # Throughput
dur = []                                   # Duration
s_rate = []                                # Success rate

config = configparser.ConfigParser()
config.read('config.cfg')

RANGE = (int)(config.get('ConfigInfo', 'RANGE'))
CAPTURE = config.get('ConfigInfo', 'CAPTURE')
IP = config.get('ConfigInfo', 'PFIOH_IP').replace('"', '')
SIZE = config.get('ConfigInfo', 'SIZE')
OP = config.get('ConfigInfo', 'OP').replace('"', '')
PATH = config.get('ConfigInfo', 'CHRIS_PATH').strip("'")
x = 0

dt = datetime.datetime.now()
r_name = "test_pfioh_request_results_%s_%s.txt" % (str(dt.date()), str(dt.time()))
results = open(r_name, "x")
results.write("METRICS: %s concurrent requests of size %s\n" % (str(RANGE), str(SIZE)))

"""
Create test files and directories to be pulled/pushed if they don't already exist                                                          
"""

test_setup.check()

if CAPTURE:
    # get PID of pfioh
    process = Popen("pgrep -f pfioh", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    PID = int(stdout)
else:
    PID = 0

for x in range(1, RANGE + 1):
    print ("iteration " + str(x))

    pfiohs = test_request(PID, 'pfioh', CAPTURE)

    for y in range(1, x + 1):
        jid = str(uuid.uuid4())
        cmd = 'bash %s/ChRIS-E2E/scripts/run_pfioh_%s %s %s /tmp/%s' % (PATH, str(OP), IP, jid, SIZE)

        pfiohs.add(cmd, jid, IP)
    
    pfiohs.start()    
    pfiohs.join()

    # Calculate resource utilization, success rate, duration, and throughput
    nums.append(x)
    s_rate.append(int(pfiohs.get_success()))
    dur.append(pfiohs.get_runtime())
    
    if CAPTURE:
        cpu.append(pfiohs.get_cpu_util())
        mem.append(pfiohs.get_mem_util())

    throughput = x / pfiohs.get_runtime()
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

########################## Graph results #######################

fig, axes = plt.subplots(nrows=2, ncols=2)
ax0, ax1, ax2, ax3 = axes.flatten()

if CAPTURE:
    ax0.plot(nums, cpu)
    ax1.plot(nums, mem)
    
ax0.bar(np.arange(RANGE), s_rate, color='r')
ax2.plot(nums, dur)
ax3.plot(nums, thr)

ax0.set_title('Success Rate')

if CAPTURE:
    ax0.set_title('CPU Utilization')
    ax1.set_title('Memory Utilization')

ax2.set_title('Duration')
ax3.set_title('Throughput')

ax0.axis([0, RANGE, 0, 400])
ax1.axis([0, RANGE, 0, 10])
ax2.axis([0, RANGE, 0, 20])
ax3.axis([0, RANGE, 0, 25])

plt.suptitle("pfioh | " + OP + " | " + SIZE + " | 1 - " + str(RANGE) + " requests/second" )

plt.show()

