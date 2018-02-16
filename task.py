# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import sys
from hoster import BaseHoster
from repo import Repository, RemoteRepository

def getTaskInstance(config, hoster):
    '''
    Get a Task instance

    :param dict config: task configuration
    :param dict hoster: hoster collection

    :return: Task object
    :rtype:  Task

    :raises ValueError: if the given configuration is invalid
    '''
    if any (key not in config for key in ['source', 'destinations']):
      raise ValueError('Missing some required properties (source, destinations)')

    if config['source'] not in hoster:
      raise ValueError('Source hoster\'' + config['source'] + '\' not found')

    if len(config['destinations']) == 0:
      raise ValueError('Not destinations specified')

    source = hoster[config['source']]
    destinations = dict()
    for destination in config['destinations']:
      if destination not in hoster:
        raise ValueError('Destination hoster \'' + destination + '\' not found')
      destinations[destination] = hoster[destination]

    if 'sync' in config:
      if config['sync'] not in ['all', 'public', 'internal', 'private', 'manual']:
        raise ValueError('sync mode \'' + config['sync'] + '\' is not supported')
      sync = config['sync']
    else:
      sync = 'manual'

    task = Task(source, destinations, sync)

    if 'create' in config and config['create'] == False:
      task.create = False
    if 'delete' in config and config['delete'] == True:
      task.delete = True
    if 'name' in config:
      task.name = config['name']

    if 'repositories' in config and len(config['repositories']) > 0:
      task.repositories = config['repositories']

    if 'ignored-repositories' in config:
      task.ignored_repositories = config['ignored-repositories']

    return task


class Task():

  def __init__(self, source, destinations, sync):
    '''
    Initialize a Task instance

    :param BaseHoster source: source hoster
    :param dict destinations: dictionary with BaseHoster as destinations
    :param str sync:          sync mode (all, public, internal, private, manual)
    '''
    self.source = source
    self.destinations = destinations
    self.sync = sync

    # Default values
    self.create = True
    self.delete = False
    self.name = None
    self.repositories = None
    self.ignored_repositories = list()


  def run(self, verbose):
    '''
    Run mirror task now. This is a blocking method!
    '''
    repositories = list()
    if self.sync == 'manual':
      if self.repositories == None:
        return
      for repo_name in self.repositories:
        if repo_name not in self.ignored_repositories:
          try:
            source_remote = self.source.getRepository(repo_name)
            if not source_remote.description.startswith('MIRROR:'):
              repository = self._createRepository(source_remote, self.destinations)
              if repository != None:
                repositories.append(repository)
          except LookupError:
            if verbose:
              print('Repository \'' + repo_name + '\' not found on \'' + self.source.name + '\'')
          except PermissionError:
            if verbose:
              print('Permission denied on hoster \'' + self.source.name + '\'')
          except Exception as e:
            if verbose:
              print('ERROR: ' + str(e))
    else:
      try:
        source_remotes = self.source.listRepositories(self.sync)
        for source_remote in source_remotes:
          if source_remote.name not in self.ignored_repositories and \
            source_remote.description != None and not source_remote.description.startswith('MIRROR:'):
            repository = self._createRepository(source_remote, self.destinations)
            if repository != None:
              repositories.append(repository)
      except LookupError:
        if verbose:
          print('Repository \'' + repo_name + '\' not found on \'' + self.source.name + '\'')
      except PermissionError:
        if verbose:
          print('Permission denied on hoster \'' + self.source.name + '\'')
          return # Skip this hoster
      except Exception as e:
        if verbose:
          print('ERROR: ' + str(e))

    for repository in repositories:
      try:
        repository.clone()
        repository.push()
      except:
        if verbose:
          print('SyncError: Skip repository \'' + repository.source.name + '\'')
        pass # ignore this repository when an error occures

    if self.delete:
      source_repositories = self.source.listRepositories('all')
      source_names = list()
      for source_repo in source_repositories:
        if source_repo.description != None and not source_repo.description.startswith('MIRROR:'):
          source_names.append(source_repo.name)

      # Delete non-existent repositories on mirror destinations
      for key in self.destinations:
        destination_repositories = self.destinations[key].listRepositories('all')
        for repo in destination_repositories:
          if repo.description != None and repo.description.startswith('MIRROR:') and not repo in source_names:
            self.destinations[key].deleteRepository(repo)
            if verbose:
              print('Repository \'' + repo.name + '\' deleted from \'' + self.destinations[key].name + '\'')


  def _createRepository(self, source_remote, destinations):
    param = {'description': source_remote.description, 'web_url': source_remote.web_url}
    description = 'MIRROR: %(description)s // Contribute at %(web_url)s' % param 

    destination_remotes = dict()
    for key in destinations:
      try:
        remote_repo = destinations[key].getRepository(source_remote.name)
        remote_repo.description = description
        remote_repo.website = source_remote.website
        destinations[key].updateRepository(remote_repo)
        destination_remotes[key] = remote_repo
      except LookupError:
        # Repository does not exist -> create it
        if self.create and source_remote.name not in destinations[key].ignored_repositories:
          try:
            destination_remotes[destinations[key].name] = destinations[key].createRepository(
              source_remote.name, source_remote.visibility, description, source_remote.web_url
            )
          except:
            pass # Skip this destination when communication errors occur
      except:
        pass # Skip this destination when communication errors occur

    if len(destination_remotes) == 0:
      return None
    return Repository(source_remote, destination_remotes)
