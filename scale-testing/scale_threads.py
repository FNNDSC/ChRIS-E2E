#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath('pman_scale'))
import time

import shlex
import subprocess
from subprocess import Popen, PIPE
import threading
import json
import time
import configparser

class scale_threads(threading.Thread):
    """
    Simple threaded class to run pman/pfioh 
    """

    def __init__(self, pname, cmd, jid, IP):
        """
        """
        
        threading.Thread.__init__(self)

        self.pname = pname
        self.cmd = cmd
        self.jid = jid
        self.IP = IP
        self.success = False
        self.stdout = ""
        self.stderr = ""
        self.CALC = False
        
        config = configparser.ConfigParser()
        config.read('config.cfg')

        self.PATH = config.get('ConfigInfo', 'CHRIS_PATH')
        
    def run(self):
        """
        """
        process = Popen(shlex.split(self.cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
        stdout, stderr = process.communicate()

        self.stdout = stdout
        self.stderr = stderr
        
        self.calc_success()

        return    
        
    def del_pvc(self):
        """
        Delete persistent volume claim (only after completion or conclusive failure of job)
        """

        del_cmd = "oc delete pvc %-storage-claim" % self.jid
        subprocess.call(del_cmd, shell=True)
        
    def get_success(self):
        """
        Return the success status of the job
        """
        if self.CALC:
            return self.success
        else:
            while (not self.CALC):
                time.sleep(2)
            return self.succees
    
    def calc_success(self):
        """
        Calculate the success status of the request
        """

        if self.pname == 'pman':
        
            status = False
            status_count = 0
        
            # Try 10 times
            
            while (status_count < 10):

                cmd = 'bash %s/ChRIS-E2E/scripts/run_pman_status %s %s' % (self.PATH, self.IP, self.jid)
                process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
                stdout, stderr = process.communicate()
                response = json.loads(stdout)

                print(response)

                if (((response['d_ret']['l_status'])[0]) == "finished"):
                    self.success = True
                    self.CALC = True
                    return
                else:
                    time.sleep(2)

                status_count += 1

            self.CALC = True
            return 

        # pfioh
        else:
            response = json.loads(self.stdout)
            if response['stdout']['status']:
                self.success = True
            self.CALC = True
            return 
                
