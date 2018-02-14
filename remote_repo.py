# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

class RemoteRepository():

  def __init__(self, id, name, visibility, description, website, git_url, web_url, source_name, user, password):
    '''
    Initialize a git remote instance
    
    :param int id:          Repository Id on the hoster API
    :param str name:        Repository name
    :param str visibility:  Repository visibility
    :param str description: Repository description
    :param str website:     Repository website
    :param str git_url:     HTTP URL to the git repository
    :param str web_url:     URL to the repository website
    :param str source_name: Name of the source hoster
    :param str user:        Username for the git hoster
    :param str password:    Password for the git hoster (in plain text)
    '''
    self.id = id
    self.git_url = git_url
    self.web_url = web_url
    self.source_name = source_name
    self.user = user
    self.password = password
    self.name = name
    self.visibility = visibility
    self.description = description
    self.website = website


  def getGitUrl(self):
    '''
    Get URL used to interact with git and the remote host

    :return: URL with authentication data for the remote repository
    :rtype: str
    '''
    param = {'user': self.user, 'password': self.password, 'url': self.git_url[8:]}
    return 'https://%(user)s:%(password)s@%(url)s' % param
