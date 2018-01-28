#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import argparse
import ipaddress
import json
from utils import *

parser = argparse.ArgumentParser(prog='gitlab-github-sync',
          description='Synchronizes repositories between GitLab and GitHub w/o direct access to the GitLab Server.')
parser.add_argument('-v', '--verbose', action="store_true",
                   help='prints more output to the console')
parser.add_argument('-c', '--config', metavar='config.json', nargs=1, type=argparse.FileType('r'),
                   default='config.json', help='path to the configuration file')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

# Read configuration file
data = json.load(args.config)

# Perform sync here...