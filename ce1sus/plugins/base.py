# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.common.debug import Log


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

PLUGIN_ROOT = 'ce1sus.plugins'


class PluginException(Exception):
  pass


def plugin_web_method(method):
  # TODO: check if the method has the right amount of arguments and the right ones
  method.web_plugin = True
  return method


def plugin_internal_method(method):
  method.web_plugin = True
  return method


class BasePlugin(object):

  def __init__(self, config):
    self.conig = config
    self.__logger = Log(config)
    self.session_manager = SessionManager(config)

  @property
  def logger(self):
    return self.__logger.get_logger(self.__class__.__name__)

  def broker_factory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    self.logger.debug('Create broker for {0}'.format(clazz))
    return self.session_manager.broker_factory(clazz)
