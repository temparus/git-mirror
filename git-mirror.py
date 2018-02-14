#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import argparse
import ipaddress
import json

from hoster import getHosterInstance
from task import getTaskInstance

parser = argparse.ArgumentParser(prog='git-mirror',
          description='Mirrors repositories from GitLab to GitHub and vice versa w/o direct access to the GitLab Server.')
parser.add_argument('-v', '--verbose', action="store_true",
                   help='prints more output to the console')
parser.add_argument('-c', '--config', metavar='config.json', nargs=1, type=argparse.FileType('r'),
                   default='config.json', help='path to the configuration file')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

# Read configuration file
data = json.load(args.config)

if 'hoster' not in data:
  raise ValueError('Configuration file does not contain any hoster')

hoster = dict()
for config in data['hoster']:
  if 'name' not in config:
    raise ValueError('Not all hoster in the configuration file have a name assigned')
  hoster[config['name']] = getHosterInstance(config)
  if args.verbose:
    print('Hoster ' + config['name'] + ' loaded')

tasks = list()
for config in data['tasks']:
  tasks.append(getTaskInstance(config, hoster))
  if args.verbose:
    print('Task ' + config['name'] + ' prepared')


for task in tasks:
  # TODO: Run tasks asynchonously
  if args.verbose:
    print('Run task ' + task.name + '...')
  task.run(args.verbose)
  if args.verbose:
    print('-----------')
