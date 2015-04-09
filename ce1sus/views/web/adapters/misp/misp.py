# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 17, 2015
"""
import cherrypy
import json

from ce1sus.controllers.common.merger import Merger
from ce1sus.controllers.events.event import EventController
from ce1sus.db.brokers.syncserverbroker import SyncServerBroker
from ce1sus.db.common.broker import IntegrityException, BrokerException
from ce1sus.helpers.common.datumzait import DatumZait
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

  def __init__(self, config, session=None):
    BaseView.__init__(self, config)
    self.event_controller = EventController(config, session)
    self.server_broker = self.event_controller.broker_factory(SyncServerBroker)
    self.ce1sus_to_misp = Ce1susMISP(config, session)
    self.login_handler = LoginHandler(config)
    self.logout_handler = LogoutHandler(config)
    self.misp_converter = MispConverter(config, None, None, None, session)
    dump = config.get('MISPAdapter', 'dump', False)
    file_loc = config.get('MISPAdapter', 'file', None)
    self.misp_converter.dump = dump
    self.misp_converter.file_location = file_loc
    self.merger = Merger(config, session)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def shadow_attributes(self, *vpath, **params):
    # this is called from the misp server to see it his know events have new proposals
    # TODO: Proposal for misp
    raise cherrypy.HTTPError(404)

  @cherrypy.expose
  def test(self):
    cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
    event = self.event_controller.get_event_by_uuid('551427fe-47ac-4247-93f0-c906950d210b')
    return self.ce1sus_to_misp.make_misp_xml(event)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET', 'POST'])
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
      detected = False
      if path[0] == 'filterEventIdsForPush':
        if method == 'POST':
          return_message = self.perform_push(body)
          detected = True
      elif path[0] == 'index':
        if method == 'GET':
          cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
          return_message = self.ce1sus_to_misp.make_index(self.get_user())
          detected = True
      if not detected:
        try:
          event_id = int(path[0])
          event = self.event_controller.get_event_by_id(event_id)
          # convert event to misp event
          cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
          misp_event = self.ce1sus_to_misp.make_misp_xml(event)
          return_message = misp_event
        except ValueError:
          raise cherrypy.HTTPError(404)
    else:
      # it is an insert of an event
      if method == 'POST':
        cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
        return_message = self.pushed_event(body)

    self.logout_handler.logout()
    return return_message

  def pushed_event(self, xml_string):
    # instantiate misp converter
    user = self.get_user()
    try:
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

            # TODO make back request also to update the event on the remote MISP
            merged_event = self.merger.merge_event(local_event, event, user)
            if merged_event:
              self.logger.info('Received Event {0} updates'.format(merged_event.uuid))
              self.event_controller.update_event(self.get_user(), merged_event, True, True)
              event = merged_event
            else:
              self.logger.info('Received Event {0} did not need to update as it is up to date'.format(event.uuid))
        except BrokerException as error:
          self.logger.error('Received a MISP Event which caused errors')
          self.logger.error(error)
          # TODO Dump xml
        return self.ce1sus_to_misp.make_misp_xml(event)
      else:
        raise cherrypy.HTTPError(405)
    except BrokerException as error:
      self.logger.error(error)
      raise cherrypy.HTTPError(404)

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
      datetime_from_string = DatumZait.utcfromtimestamp(int(date))

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
