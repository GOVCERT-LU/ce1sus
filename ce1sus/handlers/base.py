# -*- coding: utf-8 -*-

"""
module providing support for the base handler

Created: Aug, 2013
"""

from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.objects import get_class


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
    self.attribute_definitions = dict()
    self.oject_definitions = dict()

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

  def get_attriute_definition(self, chksum):
    definition = self.attribute_definitions.get(chksum, None)
    if definition:
      return definition
    else:
      raise HandlerException(u'Attribute definition with chksum {0} cannot be found')

  def get_object_definition(self, chksum):
    definition = self.attribute_definitions.get(chksum, None)
    if definition:
      return definition
    else:
      raise HandlerException(u'Attribute definition with chksum {0} cannot be found')

  def get_main_definition(self):
    """
    Returns the definition using this handler
    """
    chksums = self.get_additinal_attribute_chksums() + self.get_additional_object_chksums()
    diff = list(set(self.attribute_definitions.keys()) - set(chksums))
    if len(diff) == 1:
      main_definition = self.attribute_definitions.get(diff[0], None)
      if main_definition:
        return main_definition
      else:
        raise HandlerException((u'Error determining main definition for {0}').format(self.__class__.__name__))
    else:
      raise HandlerException((u'Could not determine main definition for {0}').format(self.__class__.__name__))

  def process(self, obj, attribute_definitions, object_definitions, user, json):
    """
    Process of the post over the RestAPI

    :param obj: parent object
    :type obj: Object
    :param definitions: The reqiried definitions
    :type definitions: List of attribute Definitions
    :param user: The user calling the function
    :type user: User
    :param rest_attribute: Attribute inserting over rest
    :type rest_attribute: ReatAttribue

    :returns: Attribute, [List of Attribute], [related_objects]
    """
    raise HandlerException(('process is not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       obj,
                                                       user,
                                                       json))

  def create_attribute(self, obj, definition, user, json):
    """
    Creates the attribute

    :param params: The parameters
    :type params: Dictionary
    :param obj: The object the attributes belongs to
    :type obj: BASE object
    :param definition: Attribute definition
    :type definition: AttributeDefinition
    :param user: The user creating the attribute
    :type user: User

    :returns: Attribute
    """
    attribute = get_class('ce1sus.db.classes.attribute', 'Attribute')()

    # Note first the definition has to be specified else the value cannot be assigned
    attribute.definition = definition

    # Note second the object has to be specified
    attribute.object = obj
    attribute.object_id = obj.identifier
    # set remaining stuff
    attribute.populate(json)
    # set the definition id as in the definition as it might get overwritten
    attribute.definition_id = definition.identifier

    return attribute

  @staticmethod
  def create_object(parent, definition, user, json):
    # TODO recreate object to new setup
    obj = get_class('ce1sus.db.classes.object', 'Object')()

    obj.identifier = None
    obj.definition = definition
    obj.event = parent.event
    obj.populate(json)
    obj.definition_id = definition.identifier
    return obj
