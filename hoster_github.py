# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

from hoster_base import BaseHoster
from remote_repo import RemoteRepository
import json
import requests
from urllib.parse import urlencode

# TODO: Implementation

class GitHubHoster(BaseHoster):

  def __init__(self, name, user, password, api_version, organization=None):
    '''
    Initialize a GitHubHoster instance

    :param str name:         hoster name
    :param str user:         username for the git service
    :param str password:     password for the git service (in plain text)
    :param int api_version:  API version
    :param str organization: organization name used for syncing
    :raises ValueError:      if the given parameters are invalid
    '''
    super().__init__(name, user, password, organization)

    if api_version not in [3]:
      raise ValueError('GitHub API v' + str(api_version) + ' is not supported')
    self.api_version = api_version


  def listRepositories(self, visibility):
    self._checkVisibility(visibility)

    param = dict()
    if visibility in ['public', 'internal' 'private']:
      if visibility == 'internal':
        visibility = 'private'
      param['visibility'] = visibility

    if self.api_version == 3:
      if self.organization != None:
        url = self._getAPIUrl('/orgs/%(org)s/repos', {'org': self.organization})
        param = {'type': visibility}
      else:
        param['affiliation'] = 'owner'
        url = self._getAPIUrl('/user/repos', {'user': self.user})
    else:
      raise ValueError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, params = param, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      repoList = list()
      for repo in response.json():
        repoList.append(self._parseProjectResponse(repo))
      return repoList
    elif response.status_code in [401, 403]:
      raise PermissionError('Access denied by the server')
    else:
      raise ConnectionError('Received HTTP error ' + str(response.status_code))


  def getRepository(self, name):
    if self.api_version == 3:
      if self.organization != None:
        param = {'name': name, 'org': self.organization}
        url = self._getAPIUrl('/search/repositories?q=%(name)s+org:%(org)s', param)
      else:
        param = {'name': name, 'user': self.user}
        url = self._getAPIUrl('/search/repositories?q=%(name)s+user:%(user)s', param)
    else:
      raise ValueError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      json_response = response.json()
      if 'items' in json_response:
        for repo in json_response['items']:
          if repo['name'] == name:
            return self._parseProjectResponse(repo)
      raise ValueError('Repository not found')
    elif response.status_code in [401, 403]:
      raise PermissionError('Access denied by the server')
    else:
      raise ConnectionError('Received HTTP error ' + str(response.status_code))


  def createRepository(self, name, visibility, description=None, website=None):
    if self.api_version == 3:

      if self.organization != None:
        url = self._getAPIUrl('/orgs/%(org)s/repos', {'org': self.organization})
      else:
        url = self._getAPIUrl('/user/repos')

      if visibility in ['internal', 'private']:
        is_private = True
      else:
        is_private = False

      values = {
        'name': name,
        'description': description,
        'homepage': website,
        'private': is_private,
        'has_issues': False,
        'has_projects': False,
        'has_wiki': False
      }
    else:
      raise ValueError('Operation not supported with API v' + str(self.api_version))

    response = requests.post(url, data = json.dumps(values), headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      return self._parseProjectResponse(response.json())
    elif response.status_code in [401, 403]:
      raise PermissionError('Access denied by the server')
    else:
      raise ConnectionError('Received HTTP error ' + str(response.status_code) + ': ' + response.text)


  def updateRepository(self, repo):
    if self.api_version == 3:
      if repo.website != None:
        repo.description += ' // ' + repo.website

      if self.organization != None:
        url = self._getAPIUrl('/repos/%(org)s/%(repo)s', {'org': self.organization, 'repo': repo.name})
      else:
        url = self._getAPIUrl('/repos/%(user)s/%(repo)s', {'user': self.user, 'repo': repo.name})

      if repo.visibility in ['internal', 'private']:
        is_private = True
      else:
        is_private = False

      values = {
        'name': repo.name,
        'description': repo.description,
        'homepage': repo.website,
        'private': is_private,
        'has_issues': False,
        'has_projects': False,
        'has_wiki': False
      }
    else:
      raise ValueError('Operation not supported with API v' + str(self.api_version))

    response = requests.patch(url, data = json.dumps(values), headers = self._getAuthenticationHeader())

    if response.status_code in [401, 403]:
      raise PermissionError('Access denied by the server')
    elif response.status_code not in [200, 201, 202]:
      raise ConnectionError('Received HTTP error ' + str(response.status_code))


  def deleteRepository(self, repo):
    if self.api_version == 3:
      if self.organization != None:
        url = self._getAPIUrl('/repos/%(org)s/%(repo)s', {'org': self.organization, 'repo': repo.name})
      else:
        url = self._getAPIUrl('/repos/%(user)s/%(repo)s', {'user': self.user, 'repo': repo.name})
    else:
      raise ValueError('Operation not supported with API v' + str(self.api_version))

    response = requests.delete(url, headers = self._getAuthenticationHeader())

    if response.status_code in [401, 403]:
      raise PermissionError('Access denied by the server')
    elif response.status_code not in [200, 201, 202, 203, 204]:
      raise ConnectionError('Received HTTP error ' + str(response.status_code))


  def _checkVisibility(self, visibility):
    if visibility not in ['all', 'public', 'internal', 'private']:
      raise ValueError('Type \'' + visibility +'\' is unknown')


  def _parseProjectResponse(self, response):
    if response['private']:
      visibility = 'private'
    else:
      visibility = 'public'

    return RemoteRepository(response['id'], response['name'], visibility, response['description'], 
      response['homepage'], response['clone_url'], response['html_url'], self.name, self.user, self.password)


  def _getAPIUrl(self, path, parameters=dict()):
    '''
    Generate the complete URL for the given parameters.

    :param str path:        Path within the API (can contain placeholders e.g. %(user_id)s)
    :param dict parameters: Values to be filled into the placeholders of the given path
    :return: Complete API URL
    :rtype:  str
    '''
    url = 'https://api.github.com'
    url += path % parameters
    return url


  def _getAuthenticationHeader(self):
    return {
      'Accept': 'application/vnd.github.v' + str(self.api_version) + '.text+json',
      'Authorization': 'token ' + self.password
    }