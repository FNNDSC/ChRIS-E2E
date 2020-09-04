#!/usr/bin/env python3  

import sys, os

sys.path.append(os.path.abspath('pman_scale'))
# sys.path.append('/home/ckaubisch/ChRIS-E2E/scale-testing/pman_scale')
import time

import shlex
import time
import test_setup
import subprocess
from subprocess import Popen, PIPE
import threading
import json
import uuid
import configparser
import numpy.random as npr
import math

# Creates test directories if they don't already exist

test_setup.check()
test_setup.clean()

config = configparser.ConfigParser()
config.read('config.cfg')

PFIOH_IP = config.get('ConfigInfo', 'PFIOH_IP')
SIZE = config.get('ConfigInfo', 'SIZE')
PATH = config.get('ConfigInfo', 'CHRIS_PATH')
PMAN_IP = config.get('ConfigInfo', 'PMAN_IP')
IMAGE = config.get('ConfigInfo', 'PLUGIN')
MAX_DELAY = (int)(config.get('ConfigInfo', 'MAX_DELAY'))


class time_threads(threading.Thread):
    """                                                                                                                                                           
    Simple threaded class to run continuous pman/pfioh requests - once the request succeeds or fails, a new request is made                                                                               
                      
    """

    def __init__(self, pname, cmd):
        """
        """

        threading.Thread.__init__(self)

        self.pname = pname
        self.cmd = cmd
        self.index = 1

        #  To be calculated
        self.success = False
        self.duration = 0
        self.RUN = True

    def stop(self):
        """
        Set RUN to False to break while loop and stop thread execution
        """
        self.RUN = False

    def run(self):
        """
        Run the given command as long as RUN is true
        """

        # dirs = []

        while (self.RUN):

            print("ITERATION")

            # generate new id for the job to be run
            new_id = (str(uuid.uuid4())).split('-')
            jid = new_id[-1]
            print("New JID is " + str(jid) + "\n")
            #   dirs.append(jid)

            # what command will we be running
            if self.pname == 'pman':
                cmd = 'bash %s/ChRIS-E2E/scripts/run_pfioh_push %s %s /tmp/%s' % (PATH, PFIOH_IP, jid, SIZE)
                process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
                stdout, stderr = process.communicate()

                # check for success; if pfioh didn't push successfully return error and do not proceed to pman

                cmd = 'bash %s/ChRIS-E2E/scripts/run_pman %s %s %s %s' % (PATH, jid, f'TestService{jid}',
                                                                          PMAN_IP, IMAGE)

            elif self.pname == 'pfioh':
                cmd = 'bash %s/ChRIS-E2E/scripts/run_pfioh_push %s %s /tmp/%s' % (PATH, PFIOH_IP, jid, SIZE)
            else:
                print("ERROR! Running neither pman nor pfioh")
                return

                # start measuring time
            start = time.time()

            # execute command
            process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
            stdout, stderr = process.communicate()

            print(stdout)
            print(stderr)

            ######### Calculate Results #########

            self.calc_success(jid, stdout)
            self.duration = time.time() - start  # an approximation since we have to wait for the status call to pman to return, we don't know exactly when the job completed. We only know when we got a successful status returned.

    def calc_success(self, jid, stdout):
        """
        """

        try:
            d = json.loads(json.loads(stdout))
        except:
            print("Some exception occurred; output could not be loaded as JSON")
            print(stdout)
            return False

        if self.pname == 'pfioh':

            status = bool(d['stdout']['status'])

            if not status:
                self.success = False
                print(d['stdout']['msg'])
                return False

            self.success = True
            return status

        elif self.pname == 'pman':

            index = 0
            wait_time = 0

            while (wait_time <= MAX_DELAY):
                index += 1
                cmd = 'bash %s/ChRIS-E2E/scripts/run_pman_status %s %s' % (PATH, PMAN_IP, jid)
                process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
                stdout, stderr = process.communicate()

                try:
                    response = json.loads(stdout)
                    if len(response['d_ret']['l_status']) and response["status"] == "finished":
                        print("Job " + str(jid) + " succeeeded!")
                        self.success = True
                        return True
                    elif len(response['d_ret']['l_status']) and response["status"] == "started":
                        print("Job " + str(jid) + " in progress")
                    else:
                        print("Job " + str(jid) + " failed or incomplete")
                except (ValueError, TypeError):
                    print("Error: problem loading response as JSON\n")
                    print(stdout)

                time.sleep(2 * math.log(index))
                wait_time += (2 * math.log(index))
                index += 1

            self.success = False
            return False
        else:
            print("Pname is not valid!")
            self.success = False
            return False

    def get_duration(self):
        """
        Return the duration of the request 
        """
        return self.duration

    def get_success(self):
        """
        Return success of request
        """
        return self.success
