# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 31, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.hash import hashSHA1
from types import ListType
from abc import abstractmethod
from dagr.helpers.objects import getFields
from os.path import basename
from importlib import import_module
from types import DictionaryType, ListType
from dagr.helpers.string import stringToDateTime, InputException
import json
import re

def __instantiateClass(className):
  module = import_module('.restclasses', 'ce1sus.api')
  clazz = getattr(module, className)
  # instantiate
  instance = clazz()
  # check if handler base is implemented
  if not isinstance(instance, RestClass):
    raise RestAPIException(('{0} does not implement '
                            + 'RestClass').format(className))
  return instance

def __populateAtomicValue(instance, key, value, makeBinary=True):
  if value == '':
    value = None
  else:
    stringValue = '{0}'.format(value)
    if (makeBinary and re.match(r'^\{.*file.*:.*\}$', stringValue)):
        # decompress file
      dictionary = json.loads(value)
      jsonFile = dictionary.get('file', None)
      if jsonFile:
        fileName = jsonFile[0]
        strData = jsonFile[1]
        value = strData.decode('base64')
    else:
      if stringValue.isdigit():
        value = eval(stringValue)
      else:
        try:
          # is it a date?
          value = stringToDateTime(stringValue)
        except InputException:
          pass
  setattr(instance, key, value)

def __setDictValue(instance, key, value, makeBinary=True):
  subkey, subvalue = getObjectData(value)
  subinstance = populateClassNamebyDict(subkey, subvalue, makeBinary)
  setattr(instance, key, subinstance)

def __setListValue(instance, key, value, makeBinary=True):
  result = list()
  for item in value:
    subkey, subvalue = getObjectData(item)
    subinstance = populateClassNamebyDict(subkey, subvalue, makeBinary)
    result.append(subinstance)
  setattr(instance, key, result)

def __populateInstanceByDict(instance, dictionary, makeBinary=True):

  for key, value in dictionary.iteritems():
    if isinstance(value, DictionaryType):
      __setDictValue(instance, key, value, makeBinary)
    elif isinstance(value, ListType):
      __setListValue(instance, key, value, makeBinary)
    else:
      __populateAtomicValue(instance, key, value, makeBinary)

def populateClassNamebyDict(clazz, dictionary, makeBinary=True):
  instance = __instantiateClass(clazz)
  __populateInstanceByDict(instance, dictionary, makeBinary=makeBinary)
  return instance

def getObjectData(dictionary):
  for key, value in dictionary.iteritems():
    if key == 'response':
      continue
    else:
      return key, value

def getData(obj):
  response = obj.get('response', None)
  if response.get('status', None) == 'OK':
    return getObjectData(obj)
  else:
    message = response.get('errors', '')[0]
    raise Ce1susAPIException(message)


def mapResponseToObject(jsonData):
  key, value = getData(jsonData)
  return populateClassNamebyDict(key, value)

def mapJSONToObject(jsonData):
  key, value = getObjectData(jsonData)
  return populateClassNamebyDict(key, value)

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

  def populate(self, dbObject, isOwner=False):
    objFields = getFields(dbObject)
    selfFields = getFields(self)
    for name in selfFields:
      if not name.startswith('_'):
        if name in objFields:
          value = getattr(dbObject, name)
          if isinstance(value, ListType):
            # if the value is a list call toRestObject on all sub items
            items = list()
            for item in value:
              items.append(item.toRestObject(isOwner))
            setattr(self, name, items)
          else:
            # if the value is a DB object
            toRestObject = getattr(value, "toRestObject", None)
            if callable(toRestObject):
                setattr(self, name, value.toRestObject(isOwner))
            else:
              # if the value is "atomic"
              setattr(self, name, value)

  @abstractmethod
  def toJSON(self, full=False, withDefinition=False):
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

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['uuid'] = self.uuid
    result[self.__class__.__name__]['title'] = self.title
    result[self.__class__.__name__]['description'] = '{0}'.format(
                                                              self.description)
    result[self.__class__.__name__]['first_seen'] = '{0}'.format(
                                                              self.first_seen.isoformat())
    if self.last_seen is None:
      self.last_seen = self.first_seen
    result[self.__class__.__name__]['last_seen'] = '{0}'.format(self.last_seen.isoformat())
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
                                            obj.toJSON(full=True,
                                                withDefinition=withDefinition
                                                )
                                            )
    result[self.__class__.__name__]['comments'] = None
    if full:
      result[self.__class__.__name__]['comments'] = list()
      for comment in self.comments:
        result[self.__class__.__name__]['comments'].append(comment.toJSON())
    result[self.__class__.__name__]['share'] = '{0}'.format(self.share)
    return result


class RestObject(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.attributes = None
    self.parent = None
    self.children = list()
    self.share = 1

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['children'] = list()

    for child in self.children:
      result[self.__class__.__name__]['children'].append(child.toJSON(
                                              full=full,
                                              withDefinition=withDefinition
                                              ))
    result[self.__class__.__name__]['definition'] = self.definition.toJSON(
                                              full=full,
                                              withDefinition=withDefinition
                                              )
    if full:
      result[self.__class__.__name__]['attributes'] = list()
      for attribute in self.attributes:
        result[self.__class__.__name__]['attributes'].append(
                                                       attribute.toJSON(
                                               full=True,
                                               withDefinition=withDefinition
                                                                       )
                                                            )
        pass
    result[self.__class__.__name__]['share'] = '{0}'.format(self.share)
    return result


class RestAttribute(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.value = None
    self.ioc = None
    self.share = 1

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['definition'] = self.definition.toJSON(
                                                full=True,
                                                withDefinition=withDefinition
                                                          )
    if isinstance(self.value, file):
      data = self.value.read()
      binaryASCII = '{0}'.format(data.encode("base64"))
      fileName = basename(self.value.name)
      value = {'file': (fileName, binaryASCII)}
    else:
      value = self.value
    result[self.__class__.__name__]['value'] = '{0}'.format(value)
    result[self.__class__.__name__]['ioc'] = '{0}'.format(self.ioc)
    result[self.__class__.__name__]['share'] = '{0}'.format(self.share)
    return result


class RestObjectDefinition(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.dbchksum = None

  @property
  def chksum(self):
    if self.dbchksum is None:
      self.dbchksum = hashSHA1(self.name)
    return self.dbchksum

  @chksum.setter
  def chksum(self, value):
    self.dbchksum = value

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    if withDefinition:
      result[self.__class__.__name__]['name'] = self.name
      result[self.__class__.__name__]['description'] = self.description

    result[self.__class__.__name__]['chksum'] = self.chksum
    return result


class RestAttributeDefinition(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.name = None
    self.description = None
    self.regex = None
    self.classIndex = None
    self.handlerIndex = None
    self.dbchksum = None

  @property
  def chksum(self):
    if self.dbchksum is None:
      key = '{0}{1}{2}{3}'.format(attribute.name,
                             attribute.regex,
                             attribute.classIndex,
                             attribute.handlerIndex)
      self.dbchksum = hashSHA1(key)
    return self.dbchksum

  @chksum.setter
  def chksum(self, value):
    self.dbchksum = value

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()

    if withDefinition:
      result[self.__class__.__name__]['name'] = self.name
      result[self.__class__.__name__]['description'] = self.description
      result[self.__class__.__name__]['regex'] = self.regex
      result[self.__class__.__name__]['classIndex'] = self.classIndex
      result[self.__class__.__name__]['handlerIndex'] = self.handlerIndex
    result[self.__class__.__name__]['chksum'] = self.chksum

    return result
