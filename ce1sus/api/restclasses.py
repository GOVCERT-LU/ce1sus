# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 31, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from abc import abstractmethod
from ce1sus.api.exceptions import RestClassException


class RestClass(object):
  """Rest object base class"""

  def get_classname(self):
    """Returns the current class name"""
    return self.__class__.__name__

  @abstractmethod
  def to_dict(self):
    """converts the object to a dictionary"""
    raise RestClassException(('ToJson is not implemented for '
                              + '{0}').format(self.get_classname()))


# pylint: disable=R0902
class RestEvent(RestClass):
  """Rest class of an event"""

  def __init__(self):
    RestClass.__init__(self)
    self.title = None
    self.description = None
    self.first_seen = None
    self.last_seen = None
    self.tlp = None
    self.risk = None
    self.analysis = None
    self.objects = list()
    self.published = None
    self.status = None
    self.uuid = None
    self.share = 1

  def __set_value(self, dictionary, attributename, value):
    """sets the value for the given attribute if existing else raise an exception"""
    if value:
      dictionary[self.get_classname()][attributename] = u'{0}'.format(value)
    else:
      raise RestClassException('{0} attribute was no set'.format(attributename))

  def __set_date_value(self, dictionary, attributename, value):
    """sets the value for the given attribute if existing else raise an exception"""
    if value:
      self.__set_value(dictionary, attributename, value.isoformat())
    else:
      raise RestClassException('{0} attribute was no set'.format(attributename))

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['uuid'] = self.uuid
    result[self.get_classname()]['title'] = self.title
    result[self.get_classname()]['description'] = u'{0}'.format(self.description)
    self.__set_date_value(result, 'first_seen', self.first_seen)
    if self.last_seen is None:
      self.last_seen = self.first_seen
    self.__set_date_value(result, 'last_seen', self.last_seen)
    self.__set_value(result, 'tlp', self.tlp)
    self.__set_value(result, 'status', self.status)
    self.__set_value(result, 'risk', self.risk)
    self.__set_value(result, 'analysis', self.analysis)
    result[self.get_classname()]['published'] = self.published
    if self.objects:
      result[self.get_classname()]['objects'] = list()
      for obj in self.objects:
        result[self.get_classname()]['objects'].append(obj.to_dict())
    else:
      result[self.get_classname()]['objects'] = None
    result[self.get_classname()]['share'] = u'{0}'.format(self.share)
    return result


class RestObject(RestClass):
  """Rest object representing an Object"""

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.attributes = None
    self.parent = None
    self.children = list()
    self.share = 1

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    if self.children:
      result[self.get_classname()]['children'] = list()
      for child in self.children:
        result[self.get_classname()]['children'].append(child.to_dict())
    else:
      result[self.get_classname()]['children'] = None
    result[self.get_classname()]['definition'] = self.definition.to_dict()

    if self.attributes:
      result[self.get_classname()]['attributes'] = list()

      for attribute in self.attributes:
        result[self.get_classname()]['attributes'].append(attribute.to_dict())
    else:
      result[self.get_classname()]['attributes'] = None

    result[self.get_classname()]['share'] = u'{0}'.format(self.share)
    return result


class RestAttribute(RestClass):
  """Rest object representing an Attribute"""

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.value = None
    self.ioc = None
    self.share = 1

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['definition'] = self.definition.to_dict()
    result[self.get_classname()]['value'] = self.value
    result[self.get_classname()]['ioc'] = u'{0}'.format(self.ioc)
    result[self.get_classname()]['share'] = u'{0}'.format(self.share)
    return result


class RestObjectDefinition(RestClass):
  """Rest object representing an ObjectDefinition"""
  # TODO: Add relationable
  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.chksum = None
    self.attributes = list()

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['name'] = self.name
    result[self.get_classname()]['description'] = self.description
    result[self.get_classname()]['chksum'] = self.chksum
    if self.attributes:
      result[self.get_classname()]['attributes'] = list()
      for attribute in self.attributes:
        result[self.get_classname()]['attributes'].append(attribute.to_dict())
    else:
      result[self.get_classname()]['attributes'] = None
    return result


class RestAttributeDefinition(RestClass):
  """Rest object representing an AttributeDefinition"""
  # TODO: Add relationable
  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.regex = None
    self.class_index = None
    self.handler_index = None
    self.chksum = None
    self.relation = 0

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['name'] = self.name
    result[self.get_classname()]['description'] = self.description
    result[self.get_classname()]['regex'] = self.regex
    result[self.get_classname()]['class_index'] = self.class_index
    result[self.get_classname()]['handler_index'] = self.handler_index
    result[self.get_classname()]['relation'] = self.relation
    result[self.get_classname()]['chksum'] = self.chksum
    return result
