# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

from abc import ABC, abstractmethod

class BaseHoster(ABC):

  @abstractmethod
  def __init__(self, name, user, password, organization=None, ignored_repositories=list()):
    '''
    Initialize a git hoster instance

    :param str name:                 Hoster name
    :param str user:                 Username for the git service
    :param str password:             Password for the git service (in plain text)
    :param str organization:         Organization name used for syncing
    :param str ignored_repositories: List of repository names to be ignored
    '''
    self.name = name
    self.user = user
    self.password = password
    self.organization = organization
    self.ignored_repositories = ignored_repositories


  @abstractmethod
  def getRepositoryList(self, visibility):
    '''
    Get all repositories of the given type

    :param str visibility: requested repository type (public, internal, private, all)

    :return: returns a list of RemoteRepository objects
    :rtype:  list

    :raises PermissionError:     if the access is denied by the server
    :raises ConnectionError:     if another HTTP error has occurred
    :raises NotImplementedError: if this operation is not implemented/supported with the given API version
    :raises ValueError:          if the given visibility is unknown
    '''
    pass


  @abstractmethod
  def getRepository(self, name):
    '''
    Get repository with the given name

    :param str name: repository name

    :return: returns a RemoteRepository object
    :rtype:  RemoteRepository

    :raises PermissionError:     if the access is denied by the server
    :raises ConnectionError:     if another HTTP error has occurred
    :raises NotImplementedError: if this operation is not implemented/supported with the given API version
    :raises ValueError:          if the repository does not exist
    '''
    pass


  @abstractmethod
  def createRepository(self, name, visibility, description=None, website=None):
    '''
    Create a new repository

    :param str name:        repository name
    :param str visibility:  repository visibility
    :param str description: repository description
    :param str website:     repository website

    :return: returns a RemoteRepository object
    :rtype:  RemoteRepository

    :raises PermissionError:     if the access is denied by the server
    :raises ConnectionError:     if another HTTP error has occurred
    :raises NotImplementedError: if this operation is not implemented/supported with the given API version
    :raises ValueError:          if the given parameters are invalid
    '''
    pass


  @abstractmethod
  def updateRepository(self, repo):
    '''
    Update an existing repository

    :param RemoteRepository repo: remote repository containing updated values

    :raises PermissionError:      if the access is denied by the server
    :raises ConnectionError:      if another HTTP error has occurred
    :raises NotImplementedError:  if this operation is not implemented/supported with the given API version
    :raises ValueError:           if the given parameters are invalid
    '''
    pass


  @abstractmethod
  def deleteRepository(self, repo):
    '''
    Delete a repository

    :param RemoteRepository repo: remote repository to be deleted

    :raises PermissionError:     if the access is denied by the server
    :raises ConnectionError:     if another HTTP error has occurred
    :raises NotImplementedError: if this operation is not implemented/supported with the given API version
    :raises ValueError:          if the given repository does not exist
    '''
    pass


  def _raisePermissionError(self, response):
    json_response = response.json()
    message = 'HTTP ERROR ' + str(response.status_code)
    if 'error' in json_response:
      message += ': ' + json_response['error']
    else:
      message += ': ' + response.text
    raise PermissionError(message)


  def _raiseConnectionError(self, response):
    json_response = response.json()
    message = 'HTTP ERROR ' + str(response.status_code)
    if 'error' in json_response:
      message += ': ' + json_response['error']
    else:
      message += ': ' + response.text
    raise ConnectionError(message)
