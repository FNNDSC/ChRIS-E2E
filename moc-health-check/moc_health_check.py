#!/usr/bin/env python3
import os
import configparser
import test_setup
import time
import pfurl
import json


class Health_Checker:
    
    # Defining all of required variables
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('moc-health-check/config.cfg')
        self.RANGE = config.get('ConfigInfo', 'MAX_ATTEMPTS')
        self.SIZE = config.get('ConfigInfo', 'SIZE')
        self.TIMEOUT = config.get('ConfigInfo', 'TIMEOUT')
        self.THRESHOLD = config.get('ConfigInfo', 'FAILURE_THRESHOLD')
        self.PATH = os.getcwd()
        self.WAIT = int(config.get('ConfigInfo', 'INITIAL_WAIT'))
        self.PMAN_URL = config.get('ConfigInfo', 'PMAN_URL')
        self.PFIOH_URL = config.get('ConfigInfo', 'PFIOH_URL')
        self.JID = config.get('ConfigInfo', 'JID')
        self.attempts = 0
        self.DIR = 'files'
        self.password = config.get('ConfigInfo', 'PASSWORD')

        # Creating sample files
        test_setup.automate(5)

        # Reentrancy testing
        self.check_job_status()

        # Creating file which would be attached to email
        self.createFile("moc-health-check/error.log")

    # Accessor methods
    def get_range(self):
        return self.RANGE
    
    def get_threshold(self):
        return self.THRESHOLD

    # Delete a pman job
    def job_delete(self):
        post_request = {   "action": "delete",
            "meta":  {
                "key": "jid",
                "value": '"' + self.JID + '"'
            }
        }

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(post_request),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PMAN_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = self.password
        )

        return (json.loads(dataComs()))
    
    # Upload data to swift 
    def run_pfioh_push(self):
        post_request = { "action": "pushPath",
        "meta": {
            "remote": {
                "key": self.JID 
                },
            "local": {
                "path":        "/tmp/" + self.DIR
                },
            "transport": {
                "mechanism":   "compress",
                "compress": {
                    "archive": "zip",
                    "unpack":   True,
                    "cleanup":  True
                    }
                }
            }
        }
        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(post_request),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (str(self.PFIOH_URL), "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = self.password
        )
        print(dataComs())
        return (json.loads(dataComs()))
    
    # Sets exponential backoff
    def backoff(self, attempt, max_value):
        return min(max_value,self.WAIT * 2 ** attempt)


    # Calculating success rate of pman & pfioh
    def prog_flow(self, RANGE, max_value, path_error_file, attempts, success_pfioh_push,success_pman_run, success_pman_status, success_pfioh_pull):

        list_functions = [self.run_pfioh_push, self.pman_run, self.run_pman_status, self.run_pfioh_pull] # contains methods which would test ChRIS framework 

        dict_functions = {self.run_pfioh_push:success_pfioh_push, self.pman_run:success_pman_run,
                        self.run_pman_status:success_pman_status, self.run_pfioh_pull:success_pfioh_pull} # variables with success rates that correspond to methods

        print("Iteration " + str(attempts))
        print("_________________")

        # Iterate through list of methods and calculate the success rate for each aspect of ChRIS framework
        for element in list_functions:
            
            if attempts > int(self.RANGE): 
                return (tuple(dict_functions.values())) # Returning success rates for each of methods

            elif self.verify(element()):
                dict_functions[element] += 1

            else:
                self.log_error(path_error_file, str(element()))
                time.sleep(self.backoff(self.attempts,max_value))
                return self.prog_flow(RANGE,max_value, path_error_file, attempts+1, dict_functions[list(dict_functions)[0]],dict_functions[list(dict_functions)[1]],dict_functions[list(dict_functions)[2]],dict_functions[list(dict_functions)[3]])

    # Run a job in Pman
    def pman_run(self):
        post_request = {   "action": "run",
            "meta":  {
                "cmd": "simpledsapp.py --prefix test- --sleepLength 0 /share/incoming /share/outgoing",
                "auid": "mochealthcheck",
                "jid": '"' + self.JID + '"',
                "threaded": True,
                "container": {
                        "target": {
                            "image" : "fnndsc/pl-simpledsapp"
                        }
                }
            }
        }

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(post_request),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PMAN_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = self.password
        )
        print(dataComs())
        return (json.loads(dataComs()))


    # Check status of job in Pman
    def run_pman_status(self):
        post_request = {   "action": "status",
            "meta":  {
                "key": "jid",
                "value": '"' + self.JID + '"'
            }
        }

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(post_request),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PMAN_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = self.password
        )
        print(dataComs())

        return (json.loads(dataComs()))

    # Downlad data from swift
    def run_pfioh_pull(self):
        post_request = {"action": "pullPath",
    "meta": {
        "remote": {
            "key":  '"' + self.JID + '"'
        },
        "local": {
            "path":         "/tmp/" + self.DIR,
            "createDir":    True
        },
        "transport": {
            "mechanism":    "compress",
            "compress": {
                "archive":  "zip",
                "unpack":   True,
                "cleanup":  True
            }
        }
    }}

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(post_request),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PFIOH_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = self.password
        )
        print(dataComs())

        return (json.loads(dataComs()))
    
    # Check if success rate is above threshold
    def conditionals(self, threshold, success_pfioh_push, success_pfioh_pull, success_pman_status, success_pman_run):
        state = True
        msg = ""
        if threshold > success_pfioh_push:
            msg = ", Pfioh Push"
            state = False
        if threshold > success_pman_run:
            msg += ", Pman Run"
            state = False
        if threshold > success_pman_status:
            msg += ", Pman Status"
            state = False
        if threshold > success_pfioh_pull:
            msg += ", Pfioh Pull"
        return state, msg
    
    
    # Check if commands executed properly
    def verify(self,result):
        try:
            if result['stdout']['status'] or result['stdout']['status'] == "finished": 
                return True
            else:
                return False
        except Exception:
            return False

    # Open a file and write to it
    def export(self, msg, file_name):
        with open(file_name, "w+") as file:
            file.write("env.DB_URL=" + '"' + msg + '"')

    # If error persists in MOC, write env variables to bash file
    def env_write(self,state, msg):
        if state==False:
            msg = msg[2:]
            self.export(msg, 'env.groovy')
            raise Exception
    
    # Log errors in file which would be used in email
    def log_error(self,file_name, error):
        with open(file_name, "w") as file:
            file.write(error)

    # Checks if job is currently running in pman
    def job_execution(self, output):
        try:
            if output['stdout']['status'] == "started":
                return True
        except Exception:
            return False
    
    # Reentrancy testing - checks if a job with specific JID is present in Pman
    def check_job_status(self):
        if self.verify(self.run_pman_status()) or self.job_execution(self.run_pman_status()):
            self.job_delete()
    
    # creates a new file
    def createFile(self, name):
        with open(name,"w+") as file:
            file.write("")
