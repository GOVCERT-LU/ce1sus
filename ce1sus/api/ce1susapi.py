# -*- coding: utf-8 -*-

"""module providing authentication"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import json
import urllib2
from types import DictionaryType, ListType
from importlib import import_module
from ce1sus.api.restclasses import RestClass, RestAPIException


def json_pretty_print(j):
  return json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))


class Ce1susAPIException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)


class Ce1susAPI(object):

  @staticmethod
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
        subkey, subvalue = Ce1susAPI.getObjectData(value)
        if hasattr(instance, key):
          subinstance = Ce1susAPI.populateClassNamebyDict(subkey, subvalue)
          setattr(instance, key, subinstance)
      elif isinstance(value, ListType):
        lsit = list()
        if hasattr(instance, key):
          for item in value:
            subkey, subvalue = Ce1susAPI.getObjectData(item)
            subinstance = Ce1susAPI.populateClassNamebyDict(subkey, subvalue)
            lsit.append(subinstance)
          setattr(instance, key, lsit)
      else:
        if value == 'None':
          value = None
        setattr(instance, key, value)

  @staticmethod
  def populateClassNamebyDict(clazz, dictionary):
    instance = Ce1susAPI.__instantiateClass(clazz)
    Ce1susAPI.__populateInstanceByDict(instance, dictionary)
    return instance

  @staticmethod
  def getObjectData(dictionary):
    for key, value in dictionary.iteritems():
      if key == 'response':
        continue
      else:
        return key, value

  @staticmethod
  def __getData(obj):
    response = obj.get('response', None)
    if response.get('status', None) == 'OK':
      return Ce1susAPI.getObjectData(obj)
    else:
      message = response.get('errors', '')[0]
      raise Ce1susAPIException(message)

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
    return Ce1susAPI.populateClassNamebyDict(key, value)

  def getEventByID(self, identifier, full=False, withDefinition=False):
    if full:
      parameters = '?showAll=1'
    else:
      parameters = ''
    if withDefinition:
      if parameters:
        parameters = parameters + '&withDefinition=1'
      else:
        parameters = '?withDefinition=1'

    result = self.__request('/event/{0}{1}'.format(identifier,
                                                   parameters),
                            None)
    return self.__mapJSONToObject(result)

  def insertEvent(self, event):
    if isinstance(event, RestClass):
      data = dict(event.toJSON(True, True))
      result = self.__request('/event/0', data)
    else:
      raise Ce1susAPIException(('Object{0} does not implement '
                                + 'RestClass').format(event))

  def getObjectByID(self, identifier, full=False, withDefinition=False):
    if full:
      parameters = '?showAll=1'
    else:
      parameters = ''
    if withDefinition:
      if parameters:
        parameters = parameters + '&withDefinition=1'
      else:
        parameters = '?withDefinition=1'

    result = self.__request('/object/{0}{1}'.format(identifier,
                                                   parameters),
                            None)
    return self.__mapJSONToObject(result)
