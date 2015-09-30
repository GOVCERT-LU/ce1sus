# -*- coding: utf-8 -*-

"""
(Description)

Created on 15 Sep 2015
"""
import cherrypy

from ce1sus.connectors.ce1susconnector import Ce1susConnectorException, Ce1susConnector
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.events import EventsController
from ce1sus.db.classes.internal.backend.processitem import ProcessType
from ce1sus.views.web.api.version3.handlers.adapters.base import AdapterHandlerBase, AdapterHandlerException
from ce1sus.views.web.api.version3.handlers.restbase import rest_method, methods, RestHandlerNotFoundException, RestHandlerException, require
from ce1sus.controllers.common.process import ProcessController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Ce1susHandler(AdapterHandlerBase):

  def __init__(self, config):
    super(Ce1susHandler, self).__init__(config)
    self.connector = Ce1susConnector(config)
    self.events_controller = self.controller_factory(EventsController)
    self.process_controller = self.controller_factory(ProcessController)

  @rest_method()
  @methods(allowed=['GET'])
  @require()
  def event(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      method = args.get('method', None)
      path = args.get('path')
      requested_object = self.parse_path(path, method)
      event_id = requested_object.get('event_id', None)
      parameters = args.get('parameters')
      if event_id:
        make_file = parameters.get('file', None)
        if make_file == '':
          cherrypy.response.headers['Content-Type'] = 'application/x-download'
          cherrypy.response.headers["Content-Disposition"] = 'attachment; filename=Event_{0}_ce1sus.json'.format(event_id)

        event = self.event_controller.get_event_by_uuid(event_id)
        self.is_instance_viewable(event, cache_object)
        self.set_event_properties_cache_object(cache_object, event)
        return event.to_dict(cache_object)

      else:
        raise RestHandlerException('Cannot be called witout a valid uuid')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def pull_all(self, server_details):
    self.connector.server_details = server_details
    # get all the new/updated events from server
    try:
      self.connector.server_details = server_details
      self.connector.login()

      events = self.connector.get_index(server_details)

      new_events = dict()
      for event in events:
        new_events[event.uuid] = event

      local_events = self.event_controller.get_event_by_uuids(new_events.keys())

      items_to_remove = list()
      items_to_update = list()
      for local_event in local_events:
        rem_event = new_events[local_event.uuid]
        if local_event.last_publish_date and rem_event.last_publish_date:
          items_to_remove.append(local_event.uuid)
          if rem_event.last_publish_date > local_event.last_publish_date:
            items_to_update.apped(local_event.uuid)
        else:
          items_to_remove.append(local_event.uuid)

      for item_to_remove in items_to_remove:
        del new_events[item_to_remove]

      # process new events
      for new_event in new_events.itervalues():
        self.process_controller.create_new_process(ProcessType.PULL, new_event.uuid, server_details.user, server_details, True)

      # process updating process
      for update_event_uuid in items_to_update:
        self.process_controller.create_new_process(ProcessType.PULL_UPDATE, update_event_uuid, server_details.user, server_details, True)

      self.connector.logout()
    except (Ce1susConnectorException) as error:
      self.connector.logout()
      raise AdapterHandlerException(error)

  def push_all(self, server_details):
    # push all the new/updated events to server according to his user
    self.connector.server_details = server_details
    try:
      events = self.events_controller.get_events(None, None, server_details.user, None)[0]
      self.connector.login()
      # get the remote ones
      rem_events = self.connector.get_index(server_details)
      rem_events_dict = dict()
      for rem_event in rem_events:
        rem_events_dict[rem_event.uuid] = rem_event

      uuids_to_push = list()
      uuids_to_push_update = list()
      for event in events:
        rem_event = rem_events_dict.get(event.uuid, None)
        if rem_event:
          if event.last_publish_date and rem_event.last_publish_date:
            if event.last_publish_date > rem_event.last_publish_date:
              uuids_to_push_update.append(event.uuid)
        else:
          uuids_to_push.append(event.uuid)

      for uuid_to_push in uuids_to_push:
        self.process_controller.create_new_process(ProcessType.PUSH, uuid_to_push, server_details.user, server_details, True)

      for uuid_to_push in uuids_to_push_update:
        self.process_controller.create_new_process(ProcessType.PUSH_UPDATE, uuid_to_push, server_details.user, server_details, True)

      self.connector.logout()
    except (Ce1susConnectorException) as error:
      self.connector.logout()
      raise AdapterHandlerException(error)
