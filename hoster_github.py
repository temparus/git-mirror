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

class GitHubHoster(BaseHoster):

  def __init__(self, name, user, password, api_version, organization=None, ignored_repositories=list()):
    '''
    Initialize a GitHubHoster instance

    :param str name:                 Hoster name
    :param str user:                 Username for the git service
    :param str password:             Password for the git service (in plain text)
    :param int api_version:          API version
    :param str organization:         Organization name used for syncing
    :param str ignored_repositories: List of repository names to be ignored
    :raises ValueError:              If the given parameters are invalid
    '''
    super().__init__(name, user, password, organization, ignored_repositories)

    if api_version not in [3]:
      raise ValueError('GitHub API v' + str(api_version) + ' is not supported')
    self.api_version = api_version


  def getRepositoryList(self, visibility):
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
        url = self._getAPIUrl('/user/%(user)/repos', {'user': self.user})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))
    
    response = requests.get(url, params = param, headers = self._getAuthenticationHeader())

    repo_list = self._parseRepositoryListResponse(response)
    next_link = self._parseLinkResponseHeader(response)

    while (next_link):
      response = requests.get(next_link, headers = self._getAuthenticationHeader())
      repo_list += self._parseRepositoryListResponse(response)
      next_link = self._parseLinkResponseHeader(response)
    return repo_list


  def getRepository(self, name):
    if name in self.ignored_repositories:
      raise LookupError('Repository \'' + name + '\' not found')

    if self.api_version == 3:
      if self.organization != None:
        param = {'name': name, 'org': self.organization}
        url = self._getAPIUrl('/search/repositories?q=%(name)s+org:%(org)s', param)
      else:
        param = {'name': name, 'user': self.user}
        url = self._getAPIUrl('/search/repositories?q=%(name)s+user:%(user)s', param)
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      json_response = response.json()
      if 'items' in json_response:
        for repo in json_response['items']:
          if repo['name'] == name:
            return self._parseProjectResponse(repo)
      raise LookupError('Repository not found')
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)


  def createRepository(self, name, visibility, description=None, website=None):
    if name in self.ignored_repositories:
      raise PermissionError('Repository name \'' + name + '\' is in ignored-list of this hoster')

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
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.post(url, data = json.dumps(values), headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      return self._parseProjectResponse(response.json())
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)


  def updateRepository(self, repo):
    if self.api_version == 3:
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
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.patch(url, data = json.dumps(values), headers = self._getAuthenticationHeader())

    if response.status_code in [401, 403]:
      self._raisePermissionError(response)
    elif response.status_code not in [200, 201, 202]:
      self._raiseConnectionError(response)


  def deleteRepository(self, repo):
    if self.api_version == 3:
      if self.organization != None:
        url = self._getAPIUrl('/repos/%(org)s/%(repo)s', {'org': self.organization, 'repo': repo.name})
      else:
        url = self._getAPIUrl('/repos/%(user)s/%(repo)s', {'user': self.user, 'repo': repo.name})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.delete(url, headers = self._getAuthenticationHeader())

    if response.status_code in [401, 403]:
      self._raisePermissionError(response)
    elif response.status_code not in [200, 201, 202, 203, 204]:
      self._raiseConnectionError(response)


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


  def _parseLinkResponseHeader(self, response):
    '''
    Parses the Link header and returns the link for the next resource if available

    :param object response: request response object

    :return: returns the link for the next page
    :rtype:  str
    '''
    links = response.headers['Link'].split(',')
    for link in links:
      partials = link.split('; ', 2)
      if (len(partials) == 2 and partials[1] == 'rel="next"'):
        return partials[0][1:-1]
    return None


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
      for repo in response.json():
        if (repo['name'] not in self.ignored_repositories):
          repo_list.append(self._parseProjectResponse(repo))
      return repo_list
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)
