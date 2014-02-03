# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 31, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.api.exceptions import Ce1susAPIException, Ce1susInvalidParameter
from dagr.helpers.hash import hashSHA1
from abc import abstractmethod
from dagr.helpers.objects import getFields
from importlib import import_module
from types import DictionaryType, ListType
from dagr.helpers.strings import stringToDateTime, InputException
import json
import re
import base64
from os.path import basename


def __instantiate_class(classname):
  module = import_module('.restclasses', 'ce1sus.api')
  clazz = getattr(module, classname)
  # instantiate
  instance = clazz()
  # check if handler base is implemented
  if not isinstance(instance, RestClass):
    raise RestAPIException(('{0} does not implement '
                            + 'RestClass').format(classname))
  return instance


def __populate_atomic_value(instance, key, value, make_binary=True):
  if value == '':
    value = None
  else:
    string_value = u'{0}'.format(value)
    if (make_binary and re.match(r'^\{.*file.*:.*\}$', string_value)):
        # decompress file
      dictionary = json.loads(value)
      json_file = dictionary.get('file', None)
      if json_file:
        filename = json_file[0]
        del filename
        str_data = json_file[1]
        value = base64.b64decode(str_data)
    else:
      if string_value.isdigit():
        value = eval(string_value)
      else:
        try:
          # is it a date?
          value = stringToDateTime(string_value)
        except InputException:
          pass
  setattr(instance, key, value)


def __set_dict_value(instance, key, value, make_binary=True):
  subkey, subvalue = get_object_data(value)
  subinstance = populate_classname_by_dict(subkey, subvalue, make_binary)
  setattr(instance, key, subinstance)


def __set_list_value(instance, key, value, make_binary=True):
  result = list()
  for item in value:
    subkey, subvalue = get_object_data(item)
    subinstance = populate_classname_by_dict(subkey, subvalue, make_binary)
    result.append(subinstance)
  setattr(instance, key, result)


def __populate_instance_by_dict(instance, dictionary, make_binary=True):

  for key, value in dictionary.iteritems():
    if isinstance(value, DictionaryType):
      __set_dict_value(instance, key, value, make_binary)
    elif isinstance(value, ListType):
      __set_list_value(instance, key, value, make_binary)
    else:
      __populate_atomic_value(instance, key, value, make_binary)


def populate_classname_by_dict(clazz, dictionary, make_binary=True):
  instance = __instantiate_class(clazz)
  __populate_instance_by_dict(instance, dictionary, make_binary=make_binary)
  return instance


def get_object_data(dictionary):
  for key, value in dictionary.iteritems():
    if key == 'response':
      continue
    else:
      return key, value


def get_data(obj):
  response = obj.get('response', None)
  if response.get('status', None) == 'OK':
    return get_object_data(obj)
  else:
    message = response.get('errors', '')[0]
    raise Ce1susAPIException(message)


def map_response_to_object(json_data):
  key, value = get_data(json_data)
  if key == 'list':
    result = list()
    for item in value:
      subkey, subvalue = get_object_data(item)
      obj = populate_classname_by_dict(subkey, subvalue)
      result.append(obj)
    return result
  else:
    return populate_classname_by_dict(key, value)


def map_json_to_object(json_data):
  if json_data:
    key, value = get_object_data(json_data)
    return populate_classname_by_dict(key, value)
  else:
    return None


class RestAPIException(Exception):
  """
  Exception base for handler exceptions
  """
  def __init__(self, message):
    Exception.__init__(self, message)


class RestClassException(Exception):
  """Broker Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)


class RestClass(object):

  def populate(self, db_object, is_owner=False, full=True):
    obj_fields = getFields(db_object)
    self_fields = getFields(self)
    for name in self_fields:
      if not name.startswith('_'):
        if name in obj_fields:
          value = getattr(db_object, name)
          if isinstance(value, ListType):
            # if the value is a list call to_rest_object_method on all sub items
            items = list()
            for item in value:
              items.append(item.to_rest_object(is_owner, full))
            setattr(self, name, items)
          else:
            # if the value is a DB object
            to_rest_object_method = getattr(value,
                                            "to_rest_object_method",
                                            None)
            if callable(to_rest_object_method):
                setattr(self, name, value.to_rest_object(is_owner, full))
            else:
              # if the value is "atomic"
              setattr(self, name, value)

  @abstractmethod
  def to_dict(self, full=False, with_definition=False):
    raise RestClassException(('ToJson is not implemented for '
                              + '{0}').format(self.__class__.__name__))


# pylint: disable=R0902
class RestEvent(RestClass):

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
    self.comments = list()
    self.published = None
    self.status = None
    self.uuid = None
    self.share = 1

  def to_dict(self, full=False, with_definition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['uuid'] = self.uuid
    result[self.__class__.__name__]['title'] = self.title
    result[self.__class__.__name__]['description'] = u'{0}'.format(
                                                              self.description)
    if self.first_seen:
      result[self.__class__.__name__]['first_seen'] = u'{0}'.format(
                                                  self.first_seen.isoformat())
    else:
      result[self.__class__.__name__]['first_seen'] = ''
    if self.last_seen is None:
      self.last_seen = self.first_seen
    if self.last_seen:
      result[self.__class__.__name__]['last_seen'] = u'{0}'.format(
                                                    self.last_seen.isoformat())
    else:
      result[self.__class__.__name__]['last_seen'] = ''
    if self.tlp is None:
      tlp = None
    else:
      if hasattr(self.tlp, 'text'):
        tlp = self.tlp.text
      else:
        tlp = self.tlp
    result[self.__class__.__name__]['tlp'] = tlp
    result[self.__class__.__name__]['published'] = self.published
    result[self.__class__.__name__]['status'] = self.status
    result[self.__class__.__name__]['risk'] = self.risk
    result[self.__class__.__name__]['analysis'] = self.analysis
    result[self.__class__.__name__]['objects'] = None
    if full:
      result[self.__class__.__name__]['objects'] = list()
      for obj in self.objects:
        result[self.__class__.__name__]['objects'].append(
                                            obj.to_dict(full=True,
                                                with_definition=with_definition
                                                )
                                            )
    result[self.__class__.__name__]['comments'] = None
    if full:
      result[self.__class__.__name__]['comments'] = list()
      for comment in self.comments:
        result[self.__class__.__name__]['comments'].append(comment.to_dict())
    result[self.__class__.__name__]['share'] = u'{0}'.format(self.share)
    return result


class RestComment(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.comment = None

  def to_dict(self, full=False, with_definition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['comment'] = self.comment

    return result


class RestObject(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.attributes = None
    self.parent = None
    self.children = list()
    self.share = 1

  def to_dict(self, full=False, with_definition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['children'] = list()

    for child in self.children:
      result[self.__class__.__name__]['children'].append(child.to_dict(
                                              full=full,
                                              with_definition=with_definition
                                              ))
    result[self.__class__.__name__]['definition'] = self.definition.to_dict(
                                              full=False,
                                              with_definition=with_definition
                                              )
    if full:
      result[self.__class__.__name__]['attributes'] = list()
      for attribute in self.attributes:
        result[self.__class__.__name__]['attributes'].append(
                                                       attribute.to_dict(
                                               full=True,
                                               with_definition=with_definition
                                                                       )
                                                            )
        pass
    result[self.__class__.__name__]['share'] = u'{0}'.format(self.share)
    return result


class RestAttribute(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.value = None
    self.ioc = None
    self.share = 1

  def to_dict(self, full=False, with_definition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['definition'] = self.definition.to_dict(
                                                full=False,
                                                with_definition=with_definition
                                                          )
    if isinstance(self.value, Ce1susWrappedFile):
      value = self.value.get_api_wrapped_value()
    else:
      value = self.value

    result[self.__class__.__name__]['value'] = u'{0}'.format(value)
    result[self.__class__.__name__]['ioc'] = u'{0}'.format(self.ioc)
    result[self.__class__.__name__]['share'] = u'{0}'.format(self.share)
    return result


class RestObjectDefinition(RestClass):
  # TODO: Add relationable
  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.dbchksum = None
    self.attributes = list()

  @property
  def chksum(self):
    if self.dbchksum is None:
      self.dbchksum = hashSHA1(self.name)
    return self.dbchksum

  @chksum.setter
  def chksum(self, value):
    self.dbchksum = value

  def to_dict(self, full=False, with_definition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    if with_definition:
      result[self.__class__.__name__]['name'] = self.name
      result[self.__class__.__name__]['description'] = self.description
    result[self.__class__.__name__]['chksum'] = self.chksum
    if full:
      result[self.__class__.__name__]['attributes'] = list()
      for attribute in self.attributes:
        result[self.__class__.__name__]['attributes'].append(attribute.to_dict(full, with_definition))
    return result


class RestAttributeDefinition(RestClass):
  # TODO: Add relationable
  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.regex = None
    self.class_index = None
    self.handler_index = None
    self.dbchksum = None
    self.objects = list()
    self.relation = 0

  @property
  def chksum(self):
    if self.dbchksum is None:
      key = u'{0}{1}{2}{3}'.format(self.attribute.name,
                                   self.attribute.regex,
                                   self.attribute.class_index,
                                   self.attribute.handler_index)
      self.dbchksum = hashSHA1(key)
    return self.dbchksum

  @chksum.setter
  def chksum(self, value):
    self.dbchksum = value

  def to_dict(self, full=False, with_definition=False):
    result = dict()
    result[self.__class__.__name__] = dict()

    if with_definition:
      result[self.__class__.__name__]['name'] = self.name
      result[self.__class__.__name__]['description'] = self.description
      result[self.__class__.__name__]['regex'] = self.regex
      result[self.__class__.__name__]['class_index'] = self.class_index
      result[self.__class__.__name__]['handler_index'] = self.handler_index
      result[self.__class__.__name__]['relation'] = self.relation
    result[self.__class__.__name__]['chksum'] = self.chksum
    if full:
      result[self.__class__.__name__]['objects'] = list()
      for obj in self.objects:
        result[self.__class__.__name__]['objects'].append(obj.to_dict(full, with_definition))
    return result


class Ce1susWrappedFile(object):
  def __init__(self, stream=None, str_=None, name=''):
    if ((stream is None and str_ is None)
            or (not stream is None and not str_ is None)):
      raise Ce1susInvalidParameter()
    elif not stream is None:
      self.value = stream.read()

      if name and not name == '':
        self.name = name
      else:
        self.name = basename(stream.name)
    elif not str_ is None:
      self.value = str_

      if name and not name == '':
        self.name = name
      else:
        self.name = hashSHA1(self.value)

  def get_base64(self):
    return base64.b64encode(self.value)

  def get_api_wrapped_value(self):
    return json.dumps({'file': (self.name, self.get_base64())})
