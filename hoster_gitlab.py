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

class GitLabHoster(BaseHoster):

  def __init__(self, name, user, access_token, api_version, domain, organization=None, ignored_repositories=None):
    '''
    Initialize a GitLab hoster instance

    :param str name:                 Hoster name
    :param str user:                 Username for the git service
    :param str access_token:         Personal access token for the user
    :param int api_version:          API version
    :param str domain:               GitLab domain
    :param str organization:         Organization name used for syncing
    :param str ignored_repositories: List of repository names to be ignored
    :raises ValueError:              If the given parameters are invalid
    '''
    super().__init__(name, user, access_token, organization, ignored_repositories)

    if api_version not in [4]:
      raise ValueError('GitLab API v' + str(api_version) + ' is not supported')
    self.api_version = api_version

    if validators.domain(domain) != True:
      raise ValueError('GitLab domain is invalid')
    self.domain = domain


  def getRepositoryList(self, visibility):
    self._checkVisibility(visibility)

    param = dict()
    if visibility in ['public', 'internal' 'private']:
      param['visibility'] = visibility

    if self.api_version == 4:
      if self.organization != None:
        url = self._getAPIUrl('/groups/%(group)s/projects', {'group': self.organization})
      else:
        url = self._getAPIUrl('/users/%(user)s/projects', {'user': self.user})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.head(url, params = param, headers = self._getAuthenticationHeader())

    repo_list = self._parseApiRepositoryListResponse(response)

    while next_url is not None:
      new_items, next_url = self._getRepositoryListKeyBasedPagination(next_url, param)
      repo_list += new_items

    return repo_list


  def getRepository(self, name):
    if name in self.ignored_repositories:
      raise LookupError('Repository \'' + name + '\' not found')

    if self.api_version == 4:
      param = {'search': name}

      if self.organization != None:
        url = self._getAPIUrl('/groups/%(group)s/projects', {'group': self.organization})
      else:
        url = self._getAPIUrl('/users/%(user)s/projects', {'user': self.user})
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, params = param, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      for repo in response.json():
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

    if self.api_version == 4:
      if website != None:
        description += ' // ' + website

      url = self._getAPIUrl('/projects')
      values = {
        'name': name, 
        'visibility': visibility,
        'description': description,
        'namespace_id': self._getNamespaceId(),
        'wiki_enabled': False,
        'jobs_enabled': False,
        'issues_enabled': False,
        'merge_requests_enabled': False,
        'snippets_enabled': False
      }
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.post(url, data = values, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      return self._parseProjectResponse(response.json())
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)


  def updateRepository(self, repo):
    if self.api_version == 4:
      if repo.website != None and len(repo.website) > 0:
        repo.description += ' // ' + repo.website

      url = self._getAPIUrl('/projects/%(id)s', {'id': repo.id})
      values = {
        'name': repo.name,
        'visibility': repo.visibility,
        'description': repo.description,
        'wiki_enabled': False,
        'jobs_enabled': False,
        'issues_enabled': False,
        'merge_requests_enabled': False,
        'snippets_enabled': False
      }
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.put(url, data = values, headers = self._getAuthenticationHeader())

    if response.status_code in [401, 403]:
      self._raisePermissionError(response)
    elif response.status_code not in [200, 201, 202]:
      self._raiseConnectionError(response)


  def deleteRepository(self, repo):
    if self.api_version == 4:
      url = self._getAPIUrl('/projects/%(id)s', {'id': repo.id})
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


  def _getNamespaceId(self):
    '''
    Get Namespace for the current user / organization

    :param RemoteRepository repo: repository instance to be deleted
    :return: namespace id
    :rtype:  int
    :raises PermissionError: if the access is denied by the server
    :raises ValueError:      if the given repository does not exist
    '''
    if self.api_version == 4:
      if self.organization != None:
        param = {'search': self.organization}
      else:
        param = {'search': self.user}

      url = self._getAPIUrl('/namespaces')
    else:
      raise NotImplementedError('Operation not supported with API v' + str(self.api_version))

    response = requests.get(url, params = param, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      for repo in response.json():
        if repo['name'] == param['search'] or repo['path'] == param['search'] or repo['full_path'] == param['search']:
          return repo['id']
      raise LookupError('Namespace not found')
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)


  def _parseProjectResponse(self, response):
    return RemoteRepository(response['id'], response['name'], response['visibility'], response['description'], None, 
      response['http_url_to_repo'], response['web_url'], self.name, self.user, self.password)


  def _getAPIUrl(self, path, parameters=dict()):
    '''
    Generate the complete URL for the given parameters.

    :param str path:        Path within the API (can contain placeholders e.g. %(user_id)s)
    :param dict parameters: Values to be filled into the placeholders of the given path
    :return: Complete API URL
    :rtype:  str
    '''
    url = 'https://' + self.domain + '/api/v' + str(self.api_version)
    url += path % parameters
    return url


  def _getAuthenticationHeader(self):
    return {'Private-Token': self.password}


  def _getRepositoryListKeyBasedPagination(self, apiUrl, params):
    '''
    Get the given page of repositories of the given type

    :param str apiUrl: prepared API URL to request the repositories
    :param dict params: request GET parameters

    :return: returns a list of RemoteRepository objects and the url for the next items
    :rtype:  Tuple[List, str]

    :raises PermissionError:     if the access is denied by the server
    :raises ConnectionError:     if another HTTP error has occurred
    '''

    response = requests.get(apiUrl, params = params, headers = self._getAuthenticationHeader())

    if response.status_code in [200, 201, 202]:
      if 'link' in response.headers:
        next_link = response.headers['link']
      else:
        next_link = None
      repo_list = self._parseApiRepositoryListResponse(response)
      return repo_list, next_link
    elif response.status_code in [401, 403]:
      self._raisePermissionError(response)
    else:
      self._raiseConnectionError(response)

  def _parseApiRepositoryListResponse(self, response):
    repo_list = list()
    for repo in response.json():
      if (repo['name'] not in self.ignored_repositories):
        repo_list.append(self._parseProjectResponse(repo))
    return repo_list
