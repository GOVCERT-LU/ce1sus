# -*- coding: utf-8 -*-

"""
module providing support for the base handler

Created: Aug, 2013
"""
from ce1sus.helpers.common.config import Configuration

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class HandlerException(Exception):
  """
  Exception base for handler exceptions
  """
  pass


class UndefinedException(HandlerException):
  pass


class HandlerBase(object):
  """
  Base class for handlers

  Note this class is pseudo abstract
  """

  def __init__(self):
    # initalize the configuration for the handle and only the for the handlers
    config = Configuration('config/handlers.conf')
    self.__config = config

  def get_config_value(self, key, default_value=None):
    return self.__config.config.get(self.__class__.__name__, key.lower(), default_value)

  @staticmethod
  def get_uuid():
    raise HandlerException('get_uuid not defined')

  @staticmethod
  def get_allowed_types():
    raise HandlerException('get_allowed_types not defined')

  @staticmethod
  def get_config():
    raise HandlerException('get_config not defined')

  @staticmethod
  def get_description():
    raise HandlerException('get_description not defined')

  def get_additinal_attribute_chksums(self):
    """
    Returns a list of additional attributes checksums required for the handling
    """
    raise HandlerException(('get_additinal_attribute_chksums not defined for {0}').format(self.__class__.__name__))

  def get_additional_object_chksums(self):
    raise HandlerException(('get_additional_object_chksums not defined for {0}').format(self.__class__.__name__))

  def _get_main_definition(self, definitions):
    """
    Returns the definition using this handler
    """
    chksums = self.get_additinal_attribute_chksums() + self.get_additional_object_chksums()
    diff = list(set(definitions.keys()) - set(chksums))
    if len(diff) == 1:
      main_definition = definitions.get(diff[0], None)
      if main_definition:
        return main_definition
      else:
        raise HandlerException((u'Error determining main definition for {0}').format(self.__class__.__name__))
    else:
      raise HandlerException((u'Could not determine main definition for {0}').format(self.__class__.__name__))

  def process(self, obj, definitions, user, group, rest_attribute):
    """
    Process of the post over the RestAPI

    :param obj: parent object
    :type obj: Object
    :param definitions: The reqiried definitions
    :type definitions: List of attribtue Definitions
    :param user: The user calling the function
    :type user: User
    :param rest_attribute: Attribute inserting over rest
    :type rest_attribute: ReatAttribue

    :returns: Attribute, [List of Attribute]
    """
    raise HandlerException(('process is not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       obj,
                                                       definitions,
                                                       user,
                                                       group,
                                                       rest_attribute))
