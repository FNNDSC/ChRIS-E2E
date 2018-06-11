#!/usr/bin/env python3

import sys, os
from scale_threads import scale_threads
import subprocess, os
from subprocess import Popen, PIPE
import time
import threading

"""
Makes a given number of push/pull requests per second to pfioh
"""

class test_request(threading.Thread):
    """                                                                                                                                                          
    Makes a given number of push/pull requests per second to pfioh
    """

    def __init__(self, pid, pname, calc): #cmd, pid, pname, nt, calc):

        threading.Thread.__init__(self)

        self.threads = []
        
        #self.cmd = cmd
        self.pid = pid
        self.pname = pname
        self.successes = []
#        self.num_threads = nt

        # To be calculated
        self.mem_util = 0
        self.cpu_util = 0
        self.runtime = 0
        self.success_rate = 0
        self.CALC = calc
        
    def add(self, cmd, jid, ip):
        """
        """
        self.threads.append(scale_threads(self.pname, cmd, jid, ip))
    
        
    def clear(self):
        """
        """
        self.threads = []

        
    def run(self):
        """
        Creates nt threads over one second such that pman is receiving nt requests per second
        """

        print("calculate is: %s" % self.CALC)

        frequency = (1.0 / len(self.threads)) 

        self.successes = []
        self.success_rate = 0 

        # Clear log
        subprocess.call('> /tmp/top.log', shell=True)
 
        # Start measuring here
        if self.CALC:
            subprocess.call(["top -p " + str(self.pid) + " -d 0.2 -b | grep " + str(self.pname) + " | awk '{print $9, $10}' >> /tmp/top.log &"], shell=True)

        birth = time.time()

        for n in self.threads:
            n.start()
            time.sleep(frequency)
            
        for t in self.threads:
            t.join()
            success = t.get_success()
            self.successes.append(success)
            if success:
                self.success_rate += 1

        # Stop measuring here
        self.runtime = time.time() - birth

        if self.CALC:
            subprocess.call("kill -9 $(pgrep top)", shell=True)

        time.sleep(1)

        # Calculate cpu utilization, memory utilization, and success rate
        if self.CALC:
            self.calc_utils()
        self.success_rate = (self.success_rate / float(len(self.threads))) * 100  #self.num_threads)) * 100

        self.clear()
        
        ####################### Print results
        
        print ("\nRESULTS:")

        if self.CALC:
            print ("CPU utilization is: " + str(self.cpu_util))
            print ("Memory utilization is: " + str(self.mem_util))

        print ("____________\n\n")
        print ("Runtime is " + str(self.runtime))
        print ("Successes: ")
        print (self.successes)
        print ("Success rate: ")
        print (self.success_rate)


    def calc_utils(self):
        """
        Calculate CPU and memory utilizations from the log file                                                                                                                     
        """

        count = 0
        cpu = []
        mem = 0

        f = open("/tmp/top.log", "r")
        for line in f:
            count += 1
            curr = line.split()
            cpu.append(float(curr[0]))
            mem += float(curr[1])
            print(line)
            
        f.close()
        print ("\n")

        self.cpu_util = max(cpu)
        self.mem_util = mem/count

    def get_cpu_util(self):
        return self.cpu_util

    def get_mem_util(self):
        return self.mem_util
        
    def get_runtime(self):
        return self.runtime

    def get_success(self):
        """
        Return success rate
        """
        return self.success_rate





