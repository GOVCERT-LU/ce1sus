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

  def populate(self, dbObject):
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
              items.append(item.toRestObject())
            setattr(self, name, items)
          else:
            # if the value is a DB object
            toRestObject = getattr(value, "toRestObject", None)
            if callable(toRestObject):
                setattr(self, name, value.toRestObject())
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

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['title'] = self.title
    result[self.__class__.__name__]['description'] = '{0}'.format(
                                                              self.description)
    result[self.__class__.__name__]['first_seen'] = '{0}'.format(
                                                              self.first_seen)
    result[self.__class__.__name__]['last_seen'] = '{0}'.format(self.last_seen)
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
    return result


class RestComment(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.comment = None

  def toJSON(self, full=False, withDefinition=False):
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
    self.children = None

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
    return result


class RestAttribute(RestClass):

  def __init__(self):
    RestClass.__init__(self)
    self.definition = None
    self.value = None
    self.ioc = None

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['definition'] = self.definition.toJSON(
                                                full=True,
                                                withDefinition=withDefinition
                                                          )
    result[self.__class__.__name__]['value'] = '{0}'.format(self.value)
    result[self.__class__.__name__]['ioc'] = '{0}'.format(self.ioc)
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
    if self.name:
      testvalue = hashSHA1(self.name)
      if testvalue == value:
        self.dbchksum = value
      else:
        self.dbchksum = None
    else:
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
    self.dbchksum = None

  @property
  def chksum(self):
    if self.dbchksum is None:
      key = '{0}{1}{2}'.format(self.name, self.regex, self.classIndex)
      self.dbchksum = hashSHA1(key)
    return self.dbchksum

  @chksum.setter
  def chksum(self, value):
    if self.name:
      key = '{0}{1}{2}'.format(self.name, self.regex, self.classIndex)
      testvalue = hashSHA1(key)
      if testvalue == value:
        self.dbchksum = value
      else:
        self.dbchksum = None
    else:
      self.dbchksum = value

  def toJSON(self, full=False, withDefinition=False):
    result = dict()
    result[self.__class__.__name__] = dict()

    if withDefinition:
      result[self.__class__.__name__]['name'] = self.name
      result[self.__class__.__name__]['description'] = self.description
      result[self.__class__.__name__]['regex'] = self.regex
      result[self.__class__.__name__]['classIndex'] = self.classIndex

    result[self.__class__.__name__]['chksum'] = self.chksum

    return result
