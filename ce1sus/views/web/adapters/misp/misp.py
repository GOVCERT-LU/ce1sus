# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 17, 2015
"""
import cherrypy
from datetime import datetime
import json

from ce1sus.controllers.common.merger import Merger
from ce1sus.controllers.events.event import EventController
from ce1sus.db.brokers.syncserverbroker import SyncServerBroker
from ce1sus.db.common.broker import IntegrityException
from ce1sus.views.web.adapters.misp.ce1susmisp import Ce1susMISP
from ce1sus.views.web.adapters.misp.mispce1sus import MispConverter
from ce1sus.views.web.api.version3.handlers.loginhandler import LoginHandler, LogoutHandler
from ce1sus.views.web.api.version3.handlers.restbase import rest_method, methods
from ce1sus.views.web.common.base import BaseView


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MISPAdapter(BaseView):

  def __init__(self, config):
    BaseView.__init__(self, config)
    self.event_controller = EventController(config)
    self.server_broker = self.event_controller.broker_factory(SyncServerBroker)
    self.ce1sus_to_misp = Ce1susMISP(config)
    self.login_handler = LoginHandler(config)
    self.logout_handler = LogoutHandler(config)
    self.misp_converter = MispConverter(config, None, None, None)
    self.merger = Merger(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  def shadow_attributes(self, **args):
    # called during pull request to get proposals and such stuff
    pass

  @cherrypy.expose
  def test(self):
    cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
    event = self.event_controller.get_event_by_uuid('551427fe-47ac-4247-93f0-c906950d210b')
    return self.ce1sus_to_misp.make_misp_xml(event)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET', 'PUT', 'POST', 'DELETE'])
  def events(self, *vpath, **params):

    headers = cherrypy.request.headers
    authkey = headers.get('Authorization')
    # reset key
    headers['key'] = authkey
    self.login_handler.login(headers=headers)

    rawbody = ''
    path = vpath
    method = cherrypy.request.method
    cl = headers.get('Content-Length', None)
    if cl:
      rawbody = cherrypy.request.body.read(int(cl))

    content_type = headers.get('Content-Type', 'application/json')
    if content_type == 'application/json':
      body = json.loads(rawbody)
    elif content_type == 'application/xml':
      body = rawbody
    else:
      raise
    # check aut else a 405 exception

    # TODO: check if user has the right
    # TODO: check if user is registred
    if len(path) > 0:
      if path[0] == 'filterEventIdsForPush':
        if method == 'POST':
          return_message = self.perform_push(body)
      if path[0] == 'index':
        if method == 'GET':
          return_message = '<?xml version="1.0" encoding="UTF-8"?><response><xml_version>2.3.0</xml_version></response><!--Please note that this XML page is a representation of the /events/index page.Because the /events/index page is paginated you will have a limited number of results.You can for example ask: /events/index/limit:999.xml to get the 999 first records.You can also sort the table by using the sort and direction parameters. For example:/events/index/sort:date/direction:desc.xmlTo export all the events at once, with their attributes, use the export functionality. -->'
    else:
      # it is an insert of an event
      if method == 'POST':
        return_message = self.pushed_event(body)

    self.logout_handler.logout()
    return return_message

  def pushed_event(self, xml_string):
    # instantiate misp converter
    user = self.get_user()
    server_details = self.server_broker.get_server_by_user_id(user.identifier)
    # check if it is a misp server else raise
    if server_details.type == 'MISP':
      self.misp_converter.api_key = server_details.user.api_key
      self.misp_converter.api_url = server_details.baseurl
      self.misp_converter.tag = server_details.name
      user = self.event_controller.user_broker.get_by_id(self.get_user().identifier)
      self.misp_converter.user = user
      merged_event = None
      try:
        event = self.misp_converter.get_event_from_xml(xml_string)
        self.logger.info('Received Event {0}'.format(event.uuid))
        self.event_controller.insert_event(self.get_user(), event, True, True)
      except IntegrityException as error:
        self.logger.debug(error)
        event = self.misp_converter.get_event_from_xml(xml_string, True)
        # merge event with existing event
        local_event = self.event_controller.get_event_by_uuid(event.uuid)
        # TODO check if user can actually merge this event
        merged_event = self.merger.merge_events(local_event, event, user)
        if merged_event:
          self.logger.info('Received Event {0} updates'.format(merged_event.uuid))
          self.event_controller.update_event(self.get_user(), merged_event, True, True)
        else:
          self.logger.info('Received Event {0} did not need to update as it is up to date'.format(event.uuid))
    else:
      raise
    # make db object
    # event = self.misp_to_ce1sus.get_event_from_xml(xml_string)
    # insert into db

    # return misp xml of the event
    # return self.ce1sus_to_misp.make_misp_xml(event)$
    return ''

  def perform_push(self, send_events):
    incomming_events = dict()

    for send_event in send_events:
      uuid = send_event['Event']['uuid']

      incomming_events[uuid] = send_event['Event']['timestamp']
    remove = list()
    # find all events matching the uuids
    local_events = self.event_controller.get_event_by_uuids(incomming_events.keys())
    for local_event in local_events:
      # check if the local events were not modified
      date = incomming_events[local_event.uuid]
      datetime_from_string = datetime.utcfromtimestamp(int(date))

      if local_event.modified_on >= datetime_from_string:
        # remove the ones which are either new or
        remove.append(local_event.uuid)
      # check if the local event is not locked -> does not exist in ours
      # TODO: implement a lock?

    result = list()

    # create array of uuids
    for key in incomming_events.iterkeys():
      if key not in remove:
        result.append(key)
    cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return json.dumps(result)
