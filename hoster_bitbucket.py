# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

from hoster_base import BaseHoster
from remote_repo import RemoteRepository
import validators
import requests
import json
from urllib.parse import urlencode
from slugify import slugify

class BitbucketHoster(BaseHoster):

  def __init__(self, name, user, access_token, api_version, team=None, ignored_repositories=None):
    '''
    Initialize a GitLab hoster instance

    :param str name:                 Hoster name
    :param str user:                 Username for the git service
    :param str access_token:         Personal access token for the user
    :param int api_version:          API version
    :param str team:                 Team name used for syncing
    :param str ignored_repositories: List of repository names to be ignored
    :raises ValueError:              If the given parameters are invalid
    '''
    super().__init__(name, user, access_token, team, ignored_repositories)

    if api_version not in [2]:
      raise ValueError('Bitbucket API v' + str(api_version) + ' is not supported')
    self.api_version = api_version


  def getRepositoryList(self, visibility):
    self._checkVisibility(visibility)

    param = dict()
    if visibility in ['internal' 'private']:
      param['q'] = 'is_private = true'

    if self.api_version == 2:
      if self.organization != None:
        url = self._getAPIUrl('/2.0/repositories/%(team)s', {'team': self.organization})
      else:
        url = self._getAPIUrl('/2.0/repositories/%(user)s', {'user': self.user})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, params = param, auth = self._getBasicAuthentication())
    repo_list = self._parseRepositoryListResponse(response)
    next_link = response.json()['next']

    while (next_link):
      response = requests.get(next_link, auth = self._getBasicAuthentication())
      repo_list += self._parseRepositoryListResponse(response)
      next_link = response.json()['next']
    return repo_list


  def getRepository(self, name):
    if name in self.ignored_repositories:
      raise LookupError('Repository \'' + name + '\' not found')

    if self.api_version == 2:
      param = {'q': 'name="%(name)s"' % {'name': name}}

      if self.organization != None:
        url = self._getAPIUrl('/2.0/repositories/%(team)s', {'team': self.organization})
      else:
        url = self._getAPIUrl('/2.0/repositories/%(user)s', {'user': self.user})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, params = param, auth = self._getBasicAuthentication())

    if response.status_code in [200, 201, 202]:
      for repo in response.json()['values']:
        if repo['name'] == name:
          return self._parseProjectResponse(repo)
      raise LookupError('Repository \'' + name + '\' not found')
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)


  def createRepository(self, name, visibility, description=None, website=None):
    if name in self.ignored_repositories:
      raise PermissionError('Repository name \'' + name + '\' is in ignored-list of this hoster')

    if self.api_version == 2:

      if visibility != 'public':
        is_private = True
      else:
        is_private = False

      if self.organization != None:
        url = self._getAPIUrl('/2.0/repositories/%(team)s/%(slug)s', {'team': self.organization, 'slug': slugify(name)})
      else:
        url = self._getAPIUrl('/2.0/repositories/%(user)s/%(slug)s', {'user': self.user, 'slug': slugify(name)})
      values = {
        'name': name,
        'is_private': is_private,
        'description': description,
        'scm': 'git',
        'has_wiki': False,
        'has_issues': False,
        'fork_policy': 'allow_forks'
      }
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.post(url, json = values, auth = self._getBasicAuthentication(), headers = {'Content-Type': 'application/json'})

    if response.status_code in [200, 201, 202]:
      return self._parseProjectResponse(response.json())
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)


  def updateRepository(self, repo):
    if self.api_version == 2:
      if repo.visibility != 'public':
        is_private = True
      else:
        is_private = False

      if self.organization != None:
        url = self._getAPIUrl('/2.0/repositories/%(team)s/%(id)s', {'team': self.organization, 'id': repo.id})
      else:
        url = self._getAPIUrl('/2.0/repositories/%(user)s/%(id)s', {'user': self.user, 'id': repo.id})
      values = {
        'name': repo.name,
        'is_private': is_private,
        'description': repo.description,
        'website': repo.website,
        'scm': 'git',
        'has_wiki': False,
        'has_issues': False,
        'fork_policy': 'allow_forks'
      }
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.put(url, json = values, auth = self._getBasicAuthentication(), headers = {'Content-Type': 'application/json'})

    if response.status_code in [401, 403]:
      self._raisePermissionError(response)
    elif response.status_code not in [200, 201, 202]:
      self._raiseConnectionError(response)


  def deleteRepository(self, repo):
    if self.api_version == 2:
      if self.organization != None:
        url = self._getAPIUrl('/2.0/repositories/%(team)s/%(slug)s', {'team': self.organization, 'id': repp.id})
      else:
        url = self._getAPIUrl('/2.0/repositories/%(user)s/%(slug)s', {'user': self.user, 'id': repo.id})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.delete(url, auth = self._getBasicAuthentication())

    if response.status_code in [401, 403]:
      self._raisePermissionError(response)
    elif response.status_code not in [200, 201, 202, 203, 204]:
      self._raiseConnectionError(response)


  def _checkVisibility(self, visibility):
    if visibility not in ['all', 'public', 'internal', 'private']:
      raise ValueError('Type \'' + visibility +'\' is unknown')


  def _parseProjectResponse(self, response):
    if response['is_private']:
      visibility = 'private'
    else:
      visibility = 'public'
    
    for link in response['links']['clone']:
      if link['name'] == 'https':
        http_url_to_repo = 'https://' + link['href'].split('@', 2)[1]

    return RemoteRepository(response['uuid'], response['name'], visibility, response['description'], response['website'], 
      http_url_to_repo, response['links']['self']['href'], self.name, self.user, self.password)


  def _getAPIUrl(self, path, parameters=dict()):
    '''
    Generate the complete URL for the given parameters.

    :param str path:        Path within the API (can contain placeholders e.g. %(user_id)s)
    :param dict parameters: Values to be filled into the placeholders of the given path
    :return: Complete API URL
    :rtype:  str
    '''
    url = 'https://api.bitbucket.org'
    url += path % parameters
    return url


  def _getBasicAuthentication(self):
    return (self.user, self.password)


  def _parseRepositoryListResponse(self, response):
    '''
    Parse the API response and return all (non-ignored) repositories as a list.

    :param object response: request response object

    :return: returns a list of RemoteRepository objects
    :rtype:  list

    :raises PermissionError:     if the access is denied by the server
    :raises ConnectionError:     if another HTTP error has occurred
    '''
    if response.status_code in [200, 201, 202]:
      repo_list = list()
      values = response.json()['values']
      for repo in values:
        if (repo['name'] not in self.ignored_repositories):
          repo_list.append(self._parseProjectResponse(repo))
      return repo_list
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)
