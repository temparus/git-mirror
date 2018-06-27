# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

from hoster_base import BaseHoster
from hoster_gitlab import GitLabHoster
from hoster_github import GitHubHoster
from hoster_bitbucket import BitbucketHoster

def getHosterInstance(config):
    '''
    Get an instance of git hoster

    :param dict config: hoster configuration

    :return: BaseHoster object
    :rtype:  BaseHoster

    :raises ValueError: if the given configuration is invalid
    '''
    if any (key not in config for key in ['type', 'name', 'user', 'password', 'api-version']):
      raise ValueError('Missing some required properties (type, name, user, password, api-version)')

    if 'organization' in config:
      organization = config['organization']
    else:
      organization = None

    if 'ignored-repositories' in config:
      ignored_repositories = config['ignored-repositories']
    else:
      ignored_repositories = list()

    if config['type'] == 'github':
      return GitHubHoster(config['name'], config['user'], config['password'], config['api-version'], organization, ignored_repositories)
    elif config['type'] == 'gitlab':
      if 'domain' not in config:
        raise ValueError('Property \'domain\' required for hoster \'gitlab\'')
      return GitLabHoster(config['name'], config['user'], config['password'], config['api-version'], \
        config['domain'], organization, ignored_repositories)
    elif config['type'] == 'bitbucket':
      return BitbucketHoster(config['name'], config['user'], config['password'], config['api-version'], organization, ignored_repositories)
    else:
      raise ValueError('Unknown hoster \'' + config['type'] + '\'')
