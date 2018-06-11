#!/usr/bin/env python3

import os
from test_time import test_time
import configparser
import test_setup
import uuid

"""
Test pfioh's durability by running it under load at given specifications
NOTES:
   * small/medium/large indicates directory size (corresponding to 1, 25, and 100MB, respectively)
   * the penultimate number x (e.g. ... % IP, x, 10) denotes the number of concurrent threads  
   * the last number y (e.g. ... % IP, 20, y) denotes the number of minutes for which to run pfioh
"""

config = configparser.ConfigParser()
config.read('config.cfg')

PATH = config.get('ConfigInfo', 'CHRIS_PATH')
SIZE = config.get('ConfigInfo', 'SIZE')
OP = config.get('ConfigInfo', 'OP')
IP = config.get('ConfigInfo', 'PFIOH_IP')
THREADS = (int)(config.get('ConfigInfo', 'RANGE'))
TIME = config.get('ConfigInfo', 'TIME')

# Create test files and directories to be pulled/pushed if they don't already exist

test_setup.check()
test_setup.clean()

new_id = (str(uuid.uuid4())).split('-')
jid = new_id[-1]

test = test_time('pfioh', 'bash %s/ChRIS-E2E/scripts/run_pfioh_push %s %s /tmp/%s' % (PATH, IP, jid, SIZE), THREADS, TIME)
test.run()
test.graph()   


