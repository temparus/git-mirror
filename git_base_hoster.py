# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

from abc import ABC, abstractmethod

class GitBaseHoster(ABC):

  def __init__(self, user, password, organization=None):
    self.user = user
    self.password = password
    self.organization = organization
    super(AbstractOperation, self).__init__()

  @abstractmethod
  def listRepositories(self, type):
    '''
    List all repositories of the given type

    :param str type: requested repository type
    :return: list containing the meta data to the repositories
    :rtype: list
    :raises PermissionError: if the access is denies by the server
    :raises ValueError: if the given type is unknown
    '''
      pass

  @abstractmethod
  def createRepository(self, name, description=None):
    '''
    Create a new repository

    :param str name: repository name
    :param str description: repository description / subtitle
    :return: returns repository meta data if successful; None otherwise
    :rtype: dict
    :raises PermissionError: if the access is denies by the server
    :raises ValueError: if the name is invalid
    '''
      pass
  
  @abstractmethod
  def deleteRepository(self, repo):
    '''
    Delete a repository

    :param dict repo: repository meta data
    :return: True - if successful; False - otherwise
    :rtype: bool
    :raises PermissionError: if the access is denies by the server
    :raises ValueError: if the given repository does not exist
    '''
      pass
  
  @abstractmethod
  def cloneRepository(self, repo):
    '''
    Clone a repository to the local file system

    :param dict repo: repository meta data
    :return: local path to repository
    :rtype: str
    :raises PermissionError: if the access is denies by the server
    :raises ValueError: if the given repository does not exist
    '''
      pass
  
  @abstractmethod
  def pullRepository(self, repo, path):
    '''
    Pull a repository which already exists on the local file system

    :param dict repo: repository meta data
    :return: True - if successful; False - otherwise
    :rtype: bool
    :raises PermissionError: if the access is denies by the server
    :raises ValueError: if the given repository does not exist (on remote or locally)
    '''
      pass
  
  @abstractmethod
  def pushRepository(self, repo, path):
    '''
    Push a repository which already exists on the local file system

    :param dict repo: repository meta data
    :return: True - if successful; False - otherwise
    :rtype: bool
    :raises PermissionError: if the access is denies by the server
    :raises ValueError: if the given repository does not exist (on remote or locally)
    '''
      pass