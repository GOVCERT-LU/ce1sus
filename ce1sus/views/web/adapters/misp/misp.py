# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 17, 2015
"""
import cherrypy
import json

from ce1sus.controllers.events.event import EventController
from ce1sus.views.web.adapters.misp.ce1susmisp import Ce1susMISP
from ce1sus.views.web.adapters.misp.mispce1sus import MispConverter
from ce1sus.views.web.common.base import BaseView


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MISPAdapter(BaseView):

  def __init__(self, config):
    self.event_controller = EventController(config)
    self.ce1sus_to_misp = Ce1susMISP(config)

  # @rest_method(default=True)
  # @methods(allowed=['GET'])
  # def shadow_attributes(self, **args):
  #  pass

  @cherrypy.expose
  def test(self):
    cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
    event = self.event_controller.get_event_by_uuid('551427fe-47ac-4247-93f0-c906950d210b')
    return self.ce1sus_to_misp.make_misp_xml(event)

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET', 'PUT', 'POST', 'DELETE'])
  def events(self, *vpath, **params):
    headers = cherrypy.request.headers
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

    authkey = headers.get('Authorization')
    # check aut else a 405 exception

    # TODO: check if user has the right
    # TODO: check if user is registred
    if len(path) > 0:
      if path[0] == 'filterEventIdsForPush':
        if method == 'POST':
          return self.perform_push(body)
      if path[0] == 'index':
        if method == 'GET':
          return '<?xml version="1.0" encoding="UTF-8"?><response><xml_version>2.3.0</xml_version></response><!--Please note that this XML page is a representation of the /events/index page.Because the /events/index page is paginated you will have a limited number of results.You can for example ask: /events/index/limit:999.xml to get the 999 first records.You can also sort the table by using the sort and direction parameters. For example:/events/index/sort:date/direction:desc.xmlTo export all the events at once, with their attributes, use the export functionality. -->'
    else:
      # it is an insert of an event
      if method == 'POST':
        return self.pushed_event(body)

  def pushed_event(self, xml_string):
    # make db object
    event = self.misp_to_ce1sus.get_event_from_xml(xml_string)
    # insert into db

    # return misp xml of the event
    return self.ce1sus_to_misp.make_misp_xml(event)

  def perform_push(self, send_events):
    incomming_events = dict()

    for send_event in send_events:
      uuid = send_event['Event']['uuid']

      incomming_events[uuid] = send_event['Event']['timestamp']
    remove = list()
    # find all events matching the uuids
    local_events = self.event_controller.get_event_by_ids(incomming_events.keys())
    for local_event in local_events:
      # check if the local events were not modified
      if not (local_event.last_publish_date < incomming_events[local_event.uuid]):
        remove.append(local_event.uuid)

        # check if the local event is not locked -> does not exist in ours

    result = list()
    # remove the ones not needed
    for item in remove:
      del incomming_events[item]

    # create array of uuids
    for key in incomming_events.iterkeys():
      result.append(key)
    cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
    return json.dumps(result)
