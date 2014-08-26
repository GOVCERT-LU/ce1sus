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
from ce1sus.api.exceptions import RestClassException, Ce1susInvalidParameter
from dagr.helpers.hash import hashSHA1
import base64
import os
import json
from datetime import datetime


class RestClass(object):
  """Rest object base class"""

  def get_classname(self):
    """Returns the current class name"""
    return self.__class__.__name__

  @abstractmethod
  def to_dict(self):
    """converts the object to a dictionary"""
    raise RestClassException((u'ToJson is not implemented for '
                              + '{0}').format(self.get_classname()))

  @staticmethod
  def convert_value(value):
    """converts the value None to '' else it will be send as None-Text"""
    if value or value == 0:
      if isinstance(value, Ce1susWrappedFile):
        return value.get_api_wrapped_value()
      if isinstance(value, datetime):
        return value.strftime('%m/%d/%Y %H:%M:%S %Z')
      return value
    else:
      return ''


class RestGroup(RestClass):
  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.uuid = None

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['name'] = RestClass.convert_value(self.name)
    result[self.get_classname()]['uuid'] = RestClass.convert_value(self.uuid)
    return result


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
    self.group = None
    self.created = None
    self.modified = None

  def __set_value(self, dictionary, attributename, value):
    """sets the value for the given attribute if existing else raise an exception"""
    if value:
      dictionary[self.get_classname()][attributename] = u'{0}'.format(value)
    else:
      raise RestClassException(u'{0} attribute was no set'.format(attributename))

  def __set_date_value(self, dictionary, attributename, value):
    """sets the value for the given attribute if existing else raise an exception"""
    if value:
      self.__set_value(dictionary, attributename, value.isoformat())
    else:
      raise RestClassException(u'{0} attribute was no set'.format(attributename))

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['uuid'] = RestClass.convert_value(self.uuid)
    result[self.get_classname()]['title'] = RestClass.convert_value(self.title)
    result[self.get_classname()]['description'] = u'{0}'.format(RestClass.convert_value(self.description))
    self.__set_date_value(result, 'first_seen', self.first_seen)

    if self.last_seen is None:
      self.last_seen = self.first_seen
    self.__set_date_value(result, 'last_seen', self.last_seen)
    self.__set_value(result, 'tlp', RestClass.convert_value(self.tlp))
    self.__set_value(result, 'status', RestClass.convert_value(self.status))
    self.__set_value(result, 'risk', RestClass.convert_value(self.risk))
    self.__set_value(result, 'analysis', RestClass.convert_value(self.analysis))
    result[self.get_classname()]['published'] = RestClass.convert_value(self.published)
    objs = list()
    if self.objects:
      for obj in self.objects:
        objs.append(obj.to_dict())
    result[self.get_classname()]['objects'] = RestClass.convert_value(objs)
    result[self.get_classname()]['share'] = u'{0}'.format(RestClass.convert_value(self.share))
    if self.group:
      result[self.get_classname()]['group'] = self.group.to_dict()
    result[self.get_classname()]['created'] = RestClass.convert_value(self.created)
    result[self.get_classname()]['modified'] = RestClass.convert_value(self.modified)
    return result


class RestObject(RestClass):
  """Rest object representing an Object"""

  def __init__(self):
    RestClass.__init__(self)
    self.definition = RestObjectDefinition()
    self.attributes = None
    self.parent = None
    self.children = list()
    self.share = 1
    self.uuid = None
    self.created = None
    self.modified = None
    self.group = None

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    children = list()
    if self.children:
      for child in self.children:
        children.append(child.to_dict())
    result[self.get_classname()]['children'] = RestClass.convert_value(children)
    result[self.get_classname()]['definition'] = self.definition.to_dict()

    attributes = list()
    if self.attributes:
      for attribute in self.attributes:
        attributes.append(attribute.to_dict())
    result[self.get_classname()]['attributes'] = RestClass.convert_value(attributes)

    result[self.get_classname()]['share'] = u'{0}'.format(RestClass.convert_value(self.share))
    result[self.get_classname()]['uuid'] = RestClass.convert_value(self.uuid)
    if self.group:
      result[self.get_classname()]['group'] = self.group.to_dict()
    result[self.get_classname()]['created'] = RestClass.convert_value(self.created)
    result[self.get_classname()]['modified'] = RestClass.convert_value(self.modified)
    return result


class RestAttribute(RestClass):
  """Rest object representing an Attribute"""

  def __init__(self):
    RestClass.__init__(self)
    self.definition = RestAttributeDefinition()
    self.value = None
    self.ioc = None
    self.share = 1
    self.uuid = None
    self.created = None
    self.modified = None
    self.group = None

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['definition'] = self.definition.to_dict()
    result[self.get_classname()]['value'] = RestClass.convert_value(self.value)
    result[self.get_classname()]['ioc'] = u'{0}'.format(RestClass.convert_value(self.ioc))
    result[self.get_classname()]['share'] = u'{0}'.format(RestClass.convert_value(self.share))
    result[self.get_classname()]['uuid'] = RestClass.convert_value(self.uuid)
    if self.group:
      result[self.get_classname()]['group'] = self.group.to_dict()
    result[self.get_classname()]['created'] = RestClass.convert_value(self.created)
    result[self.get_classname()]['modified'] = RestClass.convert_value(self.modified)
    return result


class RestObjectDefinition(RestClass):
  """Rest object representing an ObjectDefinition"""

  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.chksum = None
    self.attributes = None
    self.share = 1

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['name'] = RestClass.convert_value(self.name)
    result[self.get_classname()]['description'] = RestClass.convert_value(self.description)
    result[self.get_classname()]['chksum'] = RestClass.convert_value(self.chksum)
    attributes = list()
    if self.attributes:
      for attribute in self.attributes:
        attributes.append(attribute.to_dict())
    result[self.get_classname()]['attributes'] = RestClass.convert_value(attributes)

    result[self.get_classname()]['share'] = u'{0}'.format(RestClass.convert_value(self.share))
    return result


class RestAttributeDefinition(RestClass):
  """Rest object representing an AttributeDefinition"""

  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.regex = None
    self.class_index = None
    self.handler_uuid = None
    self.chksum = None
    self.relation = 0
    self.share = 1

  def to_dict(self):
    result = dict()
    result[self.get_classname()] = dict()
    result[self.get_classname()]['name'] = RestClass.convert_value(self.name)
    result[self.get_classname()]['description'] = RestClass.convert_value(self.description)
    result[self.get_classname()]['regex'] = RestClass.convert_value(self.regex)
    result[self.get_classname()]['class_index'] = RestClass.convert_value(self.class_index)
    result[self.get_classname()]['handler_uuid'] = RestClass.convert_value(self.handler_uuid)
    result[self.get_classname()]['relation'] = RestClass.convert_value(self.relation)
    result[self.get_classname()]['chksum'] = RestClass.convert_value(self.chksum)
    result[self.get_classname()]['share'] = u'{0}'.format(RestClass.convert_value(self.share))
    return result


class Ce1susWrappedFile(object):
  def __init__(self, stream=None, str_=None, name=''):
    if (stream is None and str_ is None) or (stream is not None and str_ is not None):
      raise Ce1susInvalidParameter()
    elif stream is not None:
      self.value = stream.read()

      if name and not name == '':
        self.name = name
      else:
        self.name = os.path.basename(stream.name)
    elif str_ is not None:
      self.value = str_

      if name and not name == '':
        self.name = name
      else:
        self.name = hashSHA1(self.value)

  def get_base64(self):
    return base64.b64encode(self.value)

  def get_api_wrapped_value(self):
    return json.dumps((self.name, self.get_base64()))
