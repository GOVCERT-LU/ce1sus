# -*- coding: utf-8 -*-

"""module providing authentication"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import json
import requests
from types import DictionaryType, ListType
from importlib import import_module
from ce1sus.api.restclasses import RestClass, RestAPIException
import os


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

  def __init__(self, apiUrl, apiKey, proxies=dict()):
    self.apiUrl = apiUrl
    self.apiKey = apiKey
    self.proxies = proxies

  @staticmethod
  def __populateInstanceByDict(instance, dictionary, makeBinary=True):
    for key, value in dictionary.iteritems():
      if isinstance(value, DictionaryType):
        subkey, subvalue = Ce1susAPI.getObjectData(value)
        if hasattr(instance, key):
          subinstance = Ce1susAPI.populateClassNamebyDict(subkey, subvalue, makeBinary)
          setattr(instance, key, subinstance)
      elif isinstance(value, ListType):
        lsit = list()
        if hasattr(instance, key):
          for item in value:
            subkey, subvalue = Ce1susAPI.getObjectData(item)
            subinstance = Ce1susAPI.populateClassNamebyDict(subkey, subvalue, makeBinary)
            lsit.append(subinstance)
          setattr(instance, key, lsit)
      else:
        if value == 'None':
          value = None
        if makeBinary and 'file' in '{0}'.format(value):
          # decompress file
          dictionary = eval(value)
          jsonFile = dictionary.get('file', None)
          if jsonFile:
            fileName = jsonFile[0]
            strData = jsonFile[1]
            value = strData.decode('base64')
        setattr(instance, key, value)

  @staticmethod
  def populateClassNamebyDict(clazz, dictionary, makeBinary=True):
    instance = Ce1susAPI.__instantiateClass(clazz)
    Ce1susAPI.__populateInstanceByDict(instance, dictionary, makeBinary=makeBinary)
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
      request = requests.post(url,
                             data=json.dumps(data),
                             headers=headers,
                             proxies=self.proxies)
    else:
      request = requests.get(url, headers=headers, proxies=self.proxies)
    if request.status_code == requests.codes.ok:
      response = request.text
    else:
      try:
        request.raise_for_status()
      except requests.exceptions.HTTPError as e:
        raise Ce1susAPIException('Error ({0})'.format(e))

    # Process custom exceptions

    jsonObj = json.loads(response)
    for item in jsonObj:
      resonseObj = jsonObj.get('response', None)
      if resonseObj :
        if resonseObj.get('status', 'ERROR') == 'ERROR':
          errorMsg = '';
          for error in resonseObj.get('errors', list()):
            for value in error.itervalues():
              errorMsg += value + '.'
          raise Ce1susAPIException(errorMsg)
        else:
          return jsonObj
    raise Ce1susAPIException('Undefined Error')

  @staticmethod
  def __mapResponseToObject(jsonData):
    key, value = Ce1susAPI.__getData(jsonData)
    return Ce1susAPI.populateClassNamebyDict(key, value)

  @staticmethod
  def __mapJSONToObject(jsonData):
    key, value = Ce1susAPI.getObjectData(jsonData)
    return Ce1susAPI.populateClassNamebyDict(key, value)

  def getEventByUUID(self, uuid, withDefinition=False):
    if withDefinition:
      headers = {'full_definitions': True}
    else:
      headers = {'full_definitions': False}

    result = self.__request('/event/{0}'.format(uuid),
                            None, headers)
    return Ce1susAPI.__mapResponseToObject(result)

  def insertEvent(self, event):
    if isinstance(event, RestClass):
      data = dict(event.toJSON(True, True))
      result = self.__request('/event', data)
      return Ce1susAPI.__mapResponseToObject(result)
    else:
      raise Ce1susAPIException(('Object{0} does not implement '
                                + 'RestClass').format(event))

  def getEvents(self,
                startDate=None,
                endDate=None,
                offset=0,
                limit=20,
                withDefinition=False,
                uuids=list()):
    if withDefinition:
      headers = {'full_definitions': True}
    else:
      headers = {'full_definitions': False}

    headers['UUID'] = uuids

    if startDate:
      headers['startdate'] = startDate
    if endDate:
      headers['enddate'] = endDate
    if offset >= 0:
      headers['page'] = offset
    if limit:
      headers['limit'] = limit

    result = self.__request('/events', None, headers)
    key, values = Ce1susAPI.__getData(result)
    result = list()
    for value in values:
      jsonData = json.loads(value)
      result.append(Ce1susAPI.__mapJSONToObject(jsonData))
    return result

  def searchEvents(self,
                   objectType,
                   objectContainsAttribute=list(),
                   startDate=None,
                   endDate=None,
                   offset=0,
                   limit=20,
                   withDefinition=False):
    if withDefinition:
      headers = {'full_definitions': True}
    else:
      headers = {'full_definitions': False}

    if startDate:
      headers['startdate'] = startDate
    if endDate:
      headers['enddate'] = endDate
    if offset >= 0:
      headers['page'] = offset
    if limit:
      headers['limit'] = limit

    headers['object_attributes'] = objectContainsAttribute
    headers['object_type'] = objectType

    result = self.__request('/search/events', None, headers)
    key, uuids = Ce1susAPI.__getData(result)
    return uuids

  def searchAttributes(self,
                       objectType,
                       objectContainsAttribute=list(),
                       filterAttributes=list(),
                       startDate=None,
                       endDate=None,
                       offset=0,
                       limit=20,
                       withDefinition=False):
    if withDefinition:
      headers = {'full_definitions': True}
    else:
      headers = {'full_definitions': False}

    if startDate:
      headers['startdate'] = startDate
    if endDate:
      headers['enddate'] = endDate
    if offset >= 0:
      headers['page'] = offset
    if limit:
      headers['limit'] = limit

    headers['object_attributes'] = objectContainsAttribute
    headers['object_type'] = objectType
    headers['attributes'] = filterAttributes

    events = list()
    result = self.__request('/search/attributes', None, headers)
    key, values = Ce1susAPI.__getData(result)
    for item in values:
      jsonObject = json.loads(item)
      for key, value in jsonObject.iteritems():
        restEvent = Ce1susAPI.populateClassNamebyDict(key, value, True)
        events.append(restEvent)

    return events



