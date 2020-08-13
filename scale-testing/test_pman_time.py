#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.abspath('../'))
from test_time import test_time
import configparser

"""
Test pman's durability by running it under load at given specifications                                                                                                            
NOTES:                                                                                                                                                                              
   * the penultimate number x (e.g. ... % IP, x, 10) denotes the number of concurrent threads                                               
   * the last number y (e.g. ... % IP, 20, y) denotes the number of minutes for which to run pman    
"""

config = configparser.ConfigParser()
config.read('config.cfg')

IP = config.get('ConfigInfo', 'PMAN_IP')
NUM_REQ = config.get('ConfigInfo', 'RANGE')
TIME = config.get('ConfigInfo', 'TIME')
IMAGE = config.get('ConfigInfo', 'PLUGIN')
PATH = config.get('ConfigInfo', 'CHRIS_PATH')

test = test_time('pman', 'bash %s/ChRIS-E2E/scripts/run_pman %s %s %s %s' % (PATH, "jid", IP,
                                                                             f'TestService101', IMAGE), int(NUM_REQ),
                 int(TIME))
test.run()
test.graph()
