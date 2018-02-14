# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import os
import subprocess
from remote_repo import RemoteRepository

class Repository():

  def __init__(self, source, destinations=dict()):
    '''
    Initialize a git repository instance

    :param RemoteRepository source: Source remote repository
    :param dict destinations:       Destination remote repositories
    '''
    self.source = source
    self.destinations = destinations
    self.local_path = None
    self._checkLocalPath()


  def clone(self):
    '''
    Clone this repository to the local disk (cache)

    :raises ConnectionError: An error has occured
    '''
    self._checkLocalPath()

    if (self.local_path != None):
      if os.path.isdir(self.local_path + '/.git'):
        self.pull()
        return

    self.local_path = self._generateLocalPath()
    print(self.local_path)
    proc = subprocess.Popen(['git', 'clone', '--mirror', self.source.getGitUrl(), self.local_path + '/.git'], stdout = subprocess.DEVNULL)

    try:
      if proc.wait() != 0:
        raise ConnectionError('Cloning repository ' + self.source.git_url + ' failed')
    except KeyboardInterrupt as e:
      proc.kill()
      raise e


  def pull(self):
    '''
    Pull this repository to the local disk (cache)

    :raises ConnectionError: if another HTTP error has occured
    '''
    if (self.local_path == None):
      self.clone()
      return

    proc = subprocess.Popen(['git', 'remote', 'update', '--prune'], cwd = self.local_path, stdout = subprocess.DEVNULL)

    try:
      if proc.wait() != 0:
        raise ConnectionError('Cloning repository ' + self.source.git_url + ' failed')
    except KeyboardInterrupt as e:
      proc.kill()
      raise e


  def push(self, remote_name=None):
    '''
    (Force) Push this repository to the named git hoster

    :param str remote_name: Hoster name (push to all destinations if None)

    :raises ConnectionError: An error has occured
    '''

    if (self.local_path == None):
      raise RuntimeError('No local copy of the repository ' + self.source.git_url + ' exists')

    self.local_path = self._generateLocalPath()

    procList = list()
    if remote_name != None:
      if remote_name not in self.destinations:
        raise RuntimeError('Remote destination \'' + remote_name + '\' not found')
      procList.append(subprocess.Popen(['git', 'push', '--mirror', self.destinations[remote_name].getGitUrl()], cwd = self.local_path, stdout = subprocess.DEVNULL))
    else:
      for _key, remote in self.destinations.items():
        procList.append(subprocess.Popen(['git', 'push', '--mirror', remote.getGitUrl()], cwd = self.local_path))
    try:
      for proc in procList:
        value = proc.wait()
        if value != 0:
          raise ConnectionError('(Error ' + str(value) + ') Pushing repository ' + self.source.git_url + ' failed')
    except InterruptedError:
      for proc in procList:
        proc.kill()
    except KeyboardInterrupt:
      for proc in procList:
        proc.kill()


  def _checkLocalPath(self):
    '''
    Check if repository already exists in cache
    '''
    path = self._generateLocalPath()
    if os.path.isdir(path) and os.path.isdir(path + '/.git'):
      self.local_path = path


  def _generateLocalPath(self):
    '''
    Generate local path for this repository

    :return: local path where the repository should be stored
    :rtype:  str
    '''
    param = {'source': self.source.source_name, 'name': self.source.name}
    return '/tmp/git-mirror/%(source)s/%(name)s' % param
