# -*- coding: utf-8 -*-

"""
(Description)

Created on 30 Sep 2015
"""
import json
import requests

from ce1sus.common.system import APP_REL
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.controllers.common.permissions import PermissionController
from ce1sus.controllers.common.updater.updater import Updater
from ce1sus.db.classes.internal.event import Event
from ce1sus.common.classes.cacheobject import CacheObject


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susConnectorException(Exception):
  pass

class ConnectionException(Ce1susConnectorException):
  pass

class ForbiddenException(Ce1susConnectorException):
  pass


class NothingFoundException(Ce1susConnectorException):
  pass


class UnkownMethodException(Ce1susConnectorException):
  pass


class Ce1susConnector(BaseController):

  def __init__(self, config, session=None):
    super(Ce1susConnector, self).__init__(config, session)
    self.config = config
    # TODO: make configurable via config
    self.proxies = {}
    self.verify_ssl = False
    self.ssl_cert = None
    self.server_details = None
    self.assembler = self.controller_factory(Assembler)
    self.updater = self.controller_factory(Updater)
    self.permission_controller = self.controller_factory(PermissionController)
    self.session = requests.Session()

  @property
  def apiKey(self):
    if self.server_details is None:
      raise Ce1susConnectorException('Server Details not set')
    return self.server_details.user.api_key

  @property
  def apiUrl(self):
    if self.server_details is None:
      raise Ce1susConnectorException('Server Details not set')
    return '{0}/REST/0.3.0'.format(self.server_details.baseurl)

  def __request(self, path, method, data=None, extra_headers=None):
    try:
      url = '{0}/{1}'.format(self.apiUrl, path)
      headers = {'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Ce1sus API server client {0}'.format(APP_REL),
                 'key': self.apiKey}
      if extra_headers:
        for key, value in extra_headers.items():
          headers[key] = value

      if method == 'GET':
        request = self.session.get(url,
                                   headers=headers,
                                   proxies=self.proxies,
                                   verify=self.verify_ssl,
                                   cert=self.ssl_cert,
                                   cookies=self.session.cookies)
      elif method == 'PUT':
        request = self.session.put(url,
                                   json.dumps(data),
                                   headers=headers,
                                   proxies=self.proxies,
                                   verify=self.verify_ssl,
                                   cert=self.ssl_cert,
                                   cookies=self.session.cookies)
      elif method == 'DELETE':
        request = self.session.delete(url,
                                      headers=headers,
                                      proxies=self.proxies,
                                      verify=self.verify_ssl,
                                      cert=self.ssl_cert,
                                      cookies=self.session.cookies)
      elif method == 'POST':
        request = self.session.post(url,
                                    json.dumps(data),
                                    headers=headers,
                                    proxies=self.proxies,
                                    verify=self.verify_ssl,
                                    cert=self.ssl_cert,
                                    cookies=self.session.cookies)
      else:
        raise UnkownMethodException(u'Method {0} is not specified can only be GET,POST,PUT or DELETE')

      if request.status_code == requests.codes.ok:
        return json.loads(request.text)
      else:
        self.__handle_exception(request)
    except requests.exceptions.RequestException as error:
      raise Ce1susConnectorException(error)
    except requests.ConnectionError as error:
      raise ConnectionException('{0}'.format(error.message))

  def __handle_exception(self, request):
    try:
      request.raise_for_status()
    except requests.exceptions.HTTPError as error:
      code, reason, message = self.__extract_message(error)
      message = u'{0} ({1})'.format(reason, message)
      if code == 403:
        raise ForbiddenException(message)
      elif code == 404:
        raise NothingFoundException(message)
      else:
        raise Ce1susConnectorException(message)

  def __extract_message(self, error):
    reason = error.message
    message = error.response.text
    code = error.response.status_code
    # "<p>An event with uuid "54f63b0f-0c98-4e74-ab95-60c718689696" already exists</p>
    try:
      pos = message.index('<p>') + 3
      message = message[pos:]
      pos = message.index('</p>')
      message = message[:pos]
    except ValueError:
      # In case the message is not parsable
      pass
    return code, reason, message

  def login(self):
    self.session = requests.Session()
    text = self.__request('/login',
                          'POST',
                          None
                          )
    return text

  def logout(self):
    text = self.__request('/logout',
                          'GET',
                          )
    if text == 'User logged out':
      self.session = requests.Session()
      return True
    else:
      return False

  def __set_complete_inflated(self, url, complete=False, inflated=False):
    if complete and not inflated:
      url = '{0}?complete=true'.format(url)
    if not complete and inflated:
      url = '{0}?inflated=true'.format(url)
    if complete and inflated:
      url = '{0}?complete=true&inflated=true'.format(url)
    return url

  def get_event_by_uuid(self, uuid, complete=False, inflated=False):
    url = '/event/{0}'.format(uuid)
    url = self.__set_complete_inflated(url, complete, inflated)
    json = self.__request(url, 'GET', None)
    if json:
      
      cache_object = self.get_cache_object()
      event = self.assembler.assemble(json, Event, None, cache_object)
      return event
    
  def get_cache_object(self):
    cache_object = CacheObject()
    cache_object.user = self.server_details.user
    cache_object.permission_controller = self.permission_controller
    cache_object.authorized_cache = {}
    cache_object.rest_insert = True
    cache_object.details=True
    cache_object.inflated=True
    cache_object.flat=True
    return cache_object
  
  def insert_event(self, event, complete=False, inflated=False):
    url = '/event'
    url = self.__set_complete_inflated(url, complete, inflated)
    cache_object = self.get_cache_object()
    json = self.__request(url,
                          'POST',
                          data=event.to_dict(cache_object)
                          )
    event = self.assembler.assemble(json, Event, None, cache_object)
    return event

  def update_event(self, event, complete=False, inflated=False):
    url = '/event/{0}'.format(event.uuid)
    url = self.__set_complete_inflated(url, complete, inflated)
    cache_object = self.get_cache_object()
    json = self.__request(url,
                          'PUT',
                          data=event.to_dict(cache_object)
                          )
    event = self.assembler.assemble(json, Event, None, cache_object)
    return event

  def get_index(self, server_details=None):
    url = '/events'
    if server_details:
      self.server_details = server_details
    url = self.__set_complete_inflated(url, False, False)
    json = self.__request(url, 'GET', None)
    events_json = json.get('data', list())
    result = list()
    cache_object = self.get_cache_object()
    for event_json in events_json:
      event = self.assembler.assemble(event_json, Event, None, cache_object)
      result.append(event)
    return result



