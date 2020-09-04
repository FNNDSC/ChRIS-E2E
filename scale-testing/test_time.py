#!/usr/bin/env python3

import sys, os
from time_threads import time_threads
import test_setup
import time
import matplotlib.pyplot as plt
import numpy as np
import uuid
import configparser
import datetime
import subprocess
from subprocess import Popen, PIPE

# Creates test directories if they don't already exist
test_setup.check()
test_setup.clean()

# Get config values
config = configparser.ConfigParser()
config.read('config.cfg')

CAPTURE = config.get('ConfigInfo', 'CAPTURE')


class test_time:
    """
    Run pman/pfioh at x requests per second for a given length of time
    """

    num_threads = []
    success_rate = []
    avg_duration = []
    avg_cpu_util = []
    avg_mem_util = []
    nums = []
    START = 0

    # Process name, command, initial number of threads, final number of threads (to scale up to), duration of test
    def __init__(self, pname, cmd, nt, time):
        """
        """

        self.pname = pname  # needs to be passed to time_threads for the sake of getting back success status because
        # returned pman & pfioh json responses are slightly different
        self.cmd = cmd
        self.num_threads = nt
        self.time = time * 60  # convert minutes --> seconds

    def run(self):
        """
        """

        global num_threads
        global success_rate
        global avg_duration
        global avg_cpu_util
        global avg_mem_util
        global nums
        global START

        num_threads = []
        success_rate = []
        avg_duration = []
        avg_cpu_util = []
        avg_mem_util = []
        nums = []
        threads = []
        START = 0

        start_time = time.time()
        count = 0
        index = 1

        print("number of threads is: %s" % self.num_threads)

        if CAPTURE:
            # Clear log
            subprocess.call('> /tmp/top.log', shell=True)

            # Start logging CPU and memory utilization                                                                                                                             
            log_cmd = "pgrep -f %s" % self.pname
            process = Popen(log_cmd, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = process.communicate()
            PID = int(stdout)
            subprocess.call(["top -p " + str(PID) + " -d 0.2 -b" + "| awk '{print $9, $10; fflush();}' >> "
                                                                   "/tmp/top.log &"], shell=True)

            # Every second, capture & log information (success rate, average duration, etc.)
        while (time.time() - start_time) < float(self.time):

            duration = 0
            successes = 0

            # Measure duration and success of each thread
            for t in threads:
                duration += t.get_duration()
                if t.get_success():
                    successes += 1

            # Scale up to num_threads
            if len(threads) < self.num_threads:
                #######
                temp_cmd = self.cmd.split(" ")
                temp_cmd[2] += str(index * 100000)
                curr_cmd = " ".join(temp_cmd)
                index += 1
                #######

                curr = time_threads(self.pname, curr_cmd)
                threads.append(curr)
                curr.start()

            nums.append(count)
            num_threads.append(len(threads))
            curr_time = time.time()

            # Calculate duration and success rate
            duration = duration / float(len(threads))

            if (duration > 0) and (START == 0):
                START = len(nums)

            try:
                successes = (successes / float(len(threads))) * 100
            except:
                successes = 0

            # Log calculations
            avg_duration.append(duration)
            success_rate.append(successes)

            ############### Print Results ###############

            print("Duration is: %s\n" % str(duration))
            print("Success rate is: %d\n" % successes)

            # Calculate & sleep for the remainder of the second so that the while loop executes once a second
            count += 1
            diff = (curr_time + 1) - time.time()
            time.sleep(diff)

        for a in threads:
            a.stop()

        for t in threads:
            t.join()

    def graph(self):
        """
        """

        global START

        dt = datetime.datetime.now()
        r_name = "test_%s_time_%s_%s.txt" % (self.pname, str(dt.date()), str(dt.time()))
        results = open(r_name, "x")

        cpu = []
        mem = 0
        cpu_util = 0
        mem_util = 0

        if CAPTURE:

            subprocess.call("kill -9 $(pgrep -f top)", shell=True)

            top_count = 0

            f = open("/tmp/top.log", "r")
            for line in f:
                try:
                    curr = line.split()
                    cpu.append(float(curr[0]))
                    mem += float(curr[1])
                    top_count += 1
                except:
                    continue

            f.close()

            try:
                cpu_util = max(cpu)
                mem_util = mem / top_count
                avg_cpu_util.append(cpu_util)
                avg_mem_util.append(mem_util)

                print("CPU is: %s\n" % cpu_util)
                print("Mem is: %s\n" % mem_util)

            except:
                pass

        dur_sum = 0
        success_sum = 0
        for x in range(START, len(nums)):
            dur_sum += avg_duration[x]
            success_sum += success_rate[x]

        dur_sum = dur_sum / len(nums)
        success_sum = success_sum / (len(nums) - START)

        print("Average duration is: %f\n" % dur_sum)
        print("Average success rate is: %f\n" % success_sum)

        results.write("CPU utilization is: %s\n" % cpu_util)
        results.write("Memory utilization is:  %s\n" % mem_util)
        results.write("Average success rate is: %f\n" % success_sum)
        results.write("Average duration is: %f\n" % dur_sum)

        results.close()

        fig, axes = plt.subplots(nrows=2, ncols=2)
        ax0, ax1, ax2, ax3 = axes.flatten()

        # ax0.plot(self.nums, self.cpu)
        # ax1.plot(nums, num_threads)
        ax2.plot(nums, avg_duration)
        ax3.plot(nums, success_rate)
        # ax3.plot(self.nums, self.thr)
        # ax0.set_title('CPU Utilization')

        # ax1.set_title('Number of Threads')
        ax2.set_title('Average Duration')
        ax3.set_title('Success Rate')

        # ax0.axis([0, self.time, 0, 400])
        # ax1.axis([0, self.time, 0, 50])
        ax2.axis([0, self.time, 0, 20])
        ax3.axis([0, self.time, 0, 150])

        plt.suptitle("" + self.pname + " | " + str(self.num_threads) + " requests/second" + " | " + str(self.time / 60)
                     + " minutes")

        plt.show()
