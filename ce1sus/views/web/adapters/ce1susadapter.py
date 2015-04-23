# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 23, 2015
"""
import json
import requests

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.assembler import Assembler
from ce1sus.controllers.events.event import EventController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susAdapterException(Exception):
  pass


class Ce1susAdapterConnectionException(Ce1susAdapterException):
  pass


class UnkownMethodException(Ce1susAdapterException):
  pass


class Ce1susAdapter(BaseController):

  def __init__(self, config, session=None):
    self.server_details = None
    self.proxies = {}
    self.verify_ssl = False
    self.ssl_cert = None
    self.session = requests.session()
    self.assembler = Assembler(config, session)
    self.event_controller = EventController(config, session)

  @property
  def apiUrl(self):
    return '{0}/REST/0.3.0'.format(self.server_details.baseurl)

  @property
  def apiKey(self):
    return self.server_details.user.api_key

  def __set_complete_inflated(self, url, complete=False, inflated=False):
    if complete and not inflated:
      url = '{0}?complete=true'.format(url)
    if not complete and inflated:
      url = '{0}?inflated=true'.format(url)
    if complete and inflated:
      url = '{0}?complete=true&inflated=true'.format(url)
    return url

  def __request(self, path, method, data=None, extra_headers=None):
    try:
      url = '{0}/{1}'.format(self.apiUrl, path)
      headers = {'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Ce1sus API client 0.11',
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
        raise UnkownMethodException(u'Mehtod {0} is not specified can only be GET,POST,PUT or DELETE')

      if request.status_code == requests.codes.ok:
        return json.loads(request.text)
      else:
        self.__handle_exception(request)
    except requests.exceptions.RequestException as error:
      raise Ce1susAdapterException(error)
    except requests.ConnectionError as error:
      raise Ce1susAdapterConnectionException('{0}'.format(error.message))

  def login(self):
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
      return True
    else:
      return False

  def get_event_by_uuid(self, uuid, complete=False, inflated=False, poponly=True):
    url = '/event/{0}'.format(uuid)
    url = self.__set_complete_inflated(url, complete, inflated)
    json = self.__request(url, 'GET', None)
    event = self.assembler.assemble_event(json, self.server_details.user, False, True, poponly)
    return event

  def insert_event(self, event, complete=False, inflated=False):
    url = '/event'
    url = self.__set_complete_inflated(url, complete, inflated)
    json = self.__request(url,
                          'POST',
                          data=event.to_dict(True, True))
    event = self.assembler.update_event(event, json, self.server_details.user, False, True)
    return event

  def update_event(self, event, complete=False, inflated=False):
    url = '/event/{0}'.format(event.uuid)
    url = self.__set_complete_inflated(url, complete, inflated)
    event_permissions = self.event_controller.get_event_user_permissions(event, self.server_details.user)
    json = self.__request(url,
                          'PUT',
                          data=event.to_dict(True, True, event_permissions, self.server_details.user))
    event = self.assembler.update_event(event, json, self.server_details.user, False, True)
    return event
