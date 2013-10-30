# -*- coding: utf-8 -*-

"""module providing authentication"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import json
import urllib2
from collections import namedtuple
from ce1sus.brokers.event.eventclasses import Event, Comment, Object, \
                                              ObjectAttributeRelation
from ce1sus.brokers.event.attributebroker import Attribute
from types import DictionaryType, ListType
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, \
                                                        AttributeDefinition
from ce1sus.brokers.permission.permissionclasses import User, Group


def json_pretty_print(j):
  return json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))

class Ce1susAPIException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class Ce1susAPI(object):

  def __init__(self, apiUrl, apiKey, proxies={}):
    self.apiUrl = apiUrl
    self.apiKey = apiKey

    self.proxies = proxies
    if len(self.proxies) > 0:
      proxy = urllib2.ProxyHandler(self.proxies)
      opener = urllib2.build_opener(proxy)
      urllib2.install_opener(opener)

  @staticmethod
  def __populateInstanceByDict(instance, dictionary):
    for key, value in dictionary.iteritems():
      if isinstance(value, DictionaryType):
        subkey, subvalue = Ce1susAPI.__getObjectData(value)
        subinstance = Ce1susAPI.__populateClassNamebyDict(subkey, subvalue)
        setattr(instance, key, subinstance)
      elif isinstance(value, ListType):
        lsit = list()
        for item in value:
          subkey, subvalue = Ce1susAPI.__getObjectData(item)
          subinstance = Ce1susAPI.__populateClassNamebyDict(subkey, subvalue)
          lsit.append(subinstance)
        setattr(instance, key, lsit)
      else:
        setattr(instance, key, value)

  @staticmethod
  def __populateClassNamebyDict(clazz, dictionary):
    instance = eval(clazz)()
    Ce1susAPI.__populateInstanceByDict(instance, dictionary)
    return instance

  @staticmethod
  def __getObjectData(dict):
    for key, value in dict.iteritems():
      if key == 'response':
        continue
      else:
        return key, value

  @staticmethod
  def __getData(obj):
    response = obj.get('response', None)
    if response.get('status', None) == 'OK':
      return Ce1susAPI.__getObjectData(obj)
    else:
      raise Ce1susAPIException(response.get('errors', None))

  def __request(self, method, data=None, extra_headers=None):
    url = '{0}/{1}'.format(self.apiUrl, method)
    headers = {'Content-Type': 'application/json; charset=utf-8',
               'key': self.apiKey}

    if extra_headers:
      for key, value in extra_headers.items():
        headers[key] = value
    if data:
      request = urllib2.Request(url, data=json.dumps(data), headers=headers)
    else:
      request = urllib2.Request(url, headers=headers)
    try:
      response = urllib2.urlopen(request).read()
    except urllib2.HTTPError as e:
      raise Ce1susAPIException('Error ({0})'.format(e.code))
    except urllib2.URLError as e:
      raise Ce1susAPIException('Error ({0})'.format(e.reason.args[1]))
    return json.loads(response)

  @staticmethod
  def __mapJSONToObject(jsonData):
    key, value = Ce1susAPI.__getData(jsonData)
    return Ce1susAPI.__populateClassNamebyDict(key, value)

  def getEventByID(self, identifier, complete=False):
    if complete:
      showAll = '?showAll=1'
    else:
      showAll = ''

    result = self.__request('/event/{0}{1}'.format(identifier,
                                                   showAll),
                            None)

    return self.__mapJSONToObject(result)

  def getObjectByID(self, identifier, complete=False):
    if complete:
      showAll = '?showAll=1'
    else:
      showAll = ''

    result = self.__request('/object/{0}{1}'.format(identifier,
                                                   showAll),
                            None)

    return self.__mapJSONToObject(result)
