# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 23, 2015
"""
import json
import requests

from ce1sus.common.checks import is_event_owner
from ce1sus.common.system import APP_REL
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.assembler import Assembler
from ce1sus.controllers.common.process import ProcessController
from ce1sus.controllers.events.event import EventController
from ce1sus.db.classes.processitem import ProcessType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susAdapterException(Exception):
  pass


class Ce1susAdapterConnectionException(Ce1susAdapterException):
  pass


class Ce1susAdapterForbiddenException(Ce1susAdapterException):
  pass


class Ce1susAdapterNothingFoundException(Ce1susAdapterException):
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
    self.process_controller = ProcessController(config, session)

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

  def __extract_message(self, error):
    reason = error.message
    message = error.response.text
    code = error.response.status_code
    """<p>An event with uuid "54f63b0f-0c98-4e74-ab95-60c718689696" already exists</p>"""
    try:
      pos = message.index('<p>') + 3
      message = message[pos:]
      pos = message.index('</p>')
      message = message[:pos]
    except ValueError:
      # In case the message is not parsable
      pass
    return code, reason, message

  def __handle_exception(self, request):
    try:
      request.raise_for_status()
    except requests.exceptions.HTTPError as error:
      code, reason, message = self.__extract_message(error)
      message = u'{0} ({1})'.format(reason, message)
      if code == 403:
        raise Ce1susAdapterForbiddenException(message)
      elif code == 404:
        raise Ce1susAdapterNothingFoundException(message)
      else:
        raise Ce1susAdapterException(message)

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

  def get_event_by_uuid(self, uuid, complete=False, inflated=False, poponly=True, json=False):
    url = '/event/{0}'.format(uuid)
    url = self.__set_complete_inflated(url, complete, inflated)
    json = self.__request(url, 'GET', None)
    if json:
      return json
    else:
      event = self.assembler.assemble_event(json, self.server_details.user, False, True, poponly)
      return event

  def insert_event(self, event, complete=False, inflated=False):
    url = '/event'
    url = self.__set_complete_inflated(url, complete, inflated)
    json = self.__request(url,
                          'POST',
                          data=event.to_dict(True, True))
    owner = is_event_owner(event, self.server_details.user)
    event = self.assembler.update_event(event, json, self.server_details.user, owner, True)
    return event

  def update_event(self, event, complete=False, inflated=False):
    url = '/event/{0}'.format(event.uuid)
    url = self.__set_complete_inflated(url, complete, inflated)
    event_permissions = self.event_controller.get_event_user_permissions(event, self.server_details.user)
    json = self.__request(url,
                          'PUT',
                          data=event.to_dict(True, True, event_permissions, self.server_details.user))
    owner = is_event_owner(event, self.server_details.user)
    event = self.assembler.update_event(event, json, self.server_details.user, owner, True)
    return event

  def get_index(self, server_details=None):
    url = '/events'
    if server_details:
      self.server_details = server_details
    url = self.__set_complete_inflated(url, False, False)
    json = self.__request(url, 'GET', None)
    events_json = json.get('data', list())
    result = list()
    for event_json in events_json:
      event = self.assembler.assemble_event(event_json, self.server_details.user, False, True, True)
      result.append(event)
    return result

  def push(self, server_details):
    try:
      self.server_details = server_details
      self.login()
      user_events = self.event_controller.get_all_for_user(server_details.user)
      # get the remote ones
      rem_events = self.get_index(server_details)
      rem_events_dict = dict()
      for rem_event in rem_events:
        rem_events_dict[rem_event.uuid] = rem_event

      uuids_to_push = list()
      for event in user_events:
        rem_event = rem_events_dict.get(event.uuid, None)
        if rem_event:
          if event.last_publish_date and rem_event.last_publish_date:
            if event.last_publish_date > rem_event.last_publish_date:
              uuids_to_push.append(event.uuid)
        else:
          uuids_to_push.append(event.uuid)

      # pass
      for uuid_to_push in uuids_to_push:
        self.process_controller.create_new_process(ProcessType.PUSH, uuid_to_push, self.server_details.user, server_details, True)
    except Ce1susAdapterException as error:
      self.logout()
      raise Ce1susAdapterException(error)
    self.logout()

  def pull(self, server_details):
    try:
      self.server_details = server_details
      self.login()
      events = self.get_index(server_details)
      event_uuids = dict()
      for event in events:
        event_uuids[event.uuid] = event

      local_events = self.event_controller.get_event_by_uuids(event_uuids.keys())

      items_to_remove = list()
      for local_event in local_events:
        rem_event = event_uuids[local_event.uuid]
        if local_event.last_publish_date and rem_event.last_publish_date:
          if rem_event.last_publish_date <= local_event.last_publish_date:
            items_to_remove.append(local_event.uuid)
        else:
          items_to_remove.append(local_event.uuid)

      for item_to_remove in items_to_remove:
        del event_uuids[item_to_remove]

      for rem_event in event_uuids.itervalues():
        self.process_controller.create_new_process(ProcessType.PULL, rem_event.uuid, server_details.user, server_details, True)
      self.logout()
      return 'OK'
    except Ce1susAdapterException as error:
      self.logout()
      raise Ce1susAdapterException(error)
