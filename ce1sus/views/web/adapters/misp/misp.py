# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 17, 2015
"""
import base64
import cherrypy
from cherrypy._cperror import HTTPError
from datetime import datetime
import json

from ce1sus.controllers.base import ControllerIntegrityException, ControllerException
from ce1sus.controllers.common.merger import Merger, MergingException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.controllers.events.event import EventController
from ce1sus.db.brokers.syncserverbroker import SyncServerBroker
from ce1sus.db.classes.processitem import ProcessType
from ce1sus.db.common.broker import BrokerException
from ce1sus.mappers.misp.ce1susmisp import Ce1susMISP
from ce1sus.mappers.misp.mispce1sus import MispConverter, MispConverterException
from ce1sus.views.web.api.version3.handlers.loginhandler import LoginHandler, LogoutHandler
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MISPAdapterException(Exception):
    pass


class MISPAdapterException405(Exception):
    pass


class MISPAdapterException409(Exception):
    pass


class MISPAdapterException500(Exception):
    pass


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
        self.process_controller = ProcessController(config, session)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @require()
    def upload_xml(self, *vpath, **params):
        try:
            input_json = self.get_json()
            filename = input_json['name']
            data = input_json['data']['data']
            xml_string = base64.b64decode(data)
            complete = params.get('complete', False)
            inflated = params.get('inflated', False)
            user = self.get_user()
            user = self.user_controller.get_user_by_username(user.username)
            if 'XML' in filename or 'xml' in filename:
                self.logger.info('Starting to import xml form file {0}'.format(filename))
                self.misp_converter.user = user
                event_uuid = self.misp_converter.get_uuid_from_event_xml(xml_string)
                try:
                    event = self.misp_converter.get_event_from_xml(xml_string, None)
                    self.logger.info('Received Event {0}'.format(event.uuid))
                    self.event_controller.insert_event(user, event, True, True)
                except ControllerIntegrityException as error:
                    local_event = self.event_controller.get_event_by_uuid(event_uuid)
                    event = self.misp_converter.get_event_from_xml(xml_string, local_event)
                    # merge event with existing event

                    if self.is_event_viewable(local_event, user):
                        event_permissions = self.get_event_user_permissions(event, user)
                        try:
                            merged_event = self.merger.merge_event(local_event, event, user, event_permissions)
                        except MergingException:
                            raise MISPAdapterException405()
                            # raise cherrypy.HTTPError(405)
                    else:
                        # TODO log the changes
                        self.logger.warning('user {0} tried to change event {1} but does not have the right to see it'.format(user.username, event.identifer))
                        raise HTTPError(403, 'Not authorized')

                    if merged_event:
                        self.logger.info('Received Event {0} updates'.format(merged_event.uuid))
                        self.event_controller.update_event(user, merged_event, True, True)
                        event = merged_event
                    else:
                        self.logger.info('Received Event {0} did not need to update as it is up to date'.format(event.uuid))
                        # Log errors however
                        self.event_controller.event_broker.do_commit()
                event_permissions = self.event_controller.get_event_user_permissions(event, user)
                cherrypy.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
                return event.to_dict(complete, inflated, event_permissions, user)
            else:
                raise HTTPError(409, 'File does not end in xml or XML')
        except MispConverterException as error:
            self.logger.error(error)
            raise HTTPError(409, 'File is not a MISP XML')
        except ControllerException as error:
            self.logger.error(error)
            raise HTTPError(400, error.message)
        except Exception as error:
            self.logger.critical(error)
            raise HTTPError(500, error.message)
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def shadow_attributes(self, *vpath, **params):
        # this is called from the misp server to see it his know events have new proposals
        # TODO: Proposal for misp
        raise cherrypy.HTTPError(404)

    def get_all_events(self, server_user):
        events = self.event_controller.get_all()
        result = list()
        for event in events:
            if event.properties.is_validated:
                if self.is_event_viewable(event, server_user):
                    result.append(event)
            else:
                if event.originating_group.identifier == server_user.group.identifier:
                    result.append(event)
        return result

    def make_index(self, server_user):
        result = self.get_all_events(server_user)
        return self.ce1sus_to_misp.make_index(result)

    def pull(self, server_details):
        # use the logged in user for these request
        if server_details.type != 'MISP':
            raise MISPAdapterException('Server {0} is not a MISP server'.format(server_details.identifier))

        self.misp_converter.api_key = server_details.user.api_key
        self.misp_converter.api_url = server_details.baseurl
        self.misp_converter.tag = server_details.name
        # TODO check if it is a pull server
        user = self.event_controller.user_broker.get_by_id(self.get_user().identifier)
        self.misp_converter.user = user

        recent_events = self.misp_converter.get_index()
        local_events = self.event_controller.get_event_by_uuids(recent_events.keys())
        items_to_remove = list()

        # find the ones do not need to be updated
        for local_event in local_events:
            values = recent_events[local_event.uuid]
            if values[1] <= local_event.last_publish_date:
                items_to_remove.append(local_event.uuid)

        for item_to_remove in items_to_remove:
            del recent_events[item_to_remove]

        for value in recent_events.itervalues():
            self.process_controller.create_new_process(ProcessType.PULL, value[0], user, server_details)

            # fetch one event from misp
            # misp_event_xml = self.misp_converter.get_xml_event(value[0])
            # make insert/merge
            # try:
            #  self.ins_merg_event(server_details, misp_event_xml)
            # except BrokerException as error:
            #  self.logger.error(error)
            # TODO dump xml or log it in browser

        return 'OK'

    def push(self, server_details):
        if server_details.type != 'MISP':
            raise MISPAdapterException('Server {0} is not a MISP server'.format(server_details.identifier))
        self.misp_converter.api_key = server_details.user.api_key
        self.misp_converter.api_url = server_details.baseurl
        self.misp_converter.tag = server_details.name
        # TODO check if it is a pull server
        user = self.event_controller.user_broker.get_by_id(self.get_user().identifier)
        self.misp_converter.user = user

        # everything is handled inside here
        return self.misp_converter.filter_event_push(self, server_details)

    def make_misp_xml(self, event, server_user):

        flat_attribtues = self.ce1sus_to_misp.relations_controller.get_flat_attributes_for_event(event)
        result = list()
        for flat_attribtue in flat_attribtues:
            if self.is_item_viewable(event, flat_attribtue, server_user) and flat_attribtue.properties.is_shareable:
                result.append(flat_attribtue)

        references = list()
        for report in event.reports:
            for reference in report.references:
                if self.is_item_viewable(event, reference, server_user) and reference.properties.is_shareable:
                    references.append(reference)
        result = self.ce1sus_to_misp.create_event_xml(event, result, references)
        return result

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    def events(self, *vpath, **params):

        headers = cherrypy.request.headers
        authkey = headers.get('Authorization')

        # reset key
        headers['key'] = authkey
        self.login_handler.login(headers=headers)
        # does not handle sessions well :P
        try:
            server_user = self.event_controller.user_broker.get_user_by_api_key(authkey)
        except BrokerException as error:
            self.logger.error(error)
            raise cherrypy.HTTPError(403)

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

        if len(path) > 0:
            detected = False
            if path[0] == 'filterEventIdsForPush':
                if method == 'POST':
                    return_message = self.perform_push(body)
                    detected = True
            elif path[0] == 'index':
                if method == 'GET':
                    cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
                    return_message = self.make_index(server_user)
                    detected = True
            if not detected:
                try:
                    event_id = int(path[0])
                    event = self.event_controller.get_event_by_id(event_id)
                    self.is_event_viewable(event, server_user)
                    # TODO check if user can view event
                    # convert event to misp event
                    cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
                    misp_event = self.make_misp_xml(event, server_user)
                    return_message = misp_event
                except ValueError:
                    raise cherrypy.HTTPError(404)
        else:
            # it is an insert of an event
            if method == 'POST':
                cherrypy.response.headers['Content-Type'] = 'application/xml; charset=UTF-8'
                return_message = self.pushed_event(body, server_user)

        self.logout_handler.logout()
        return return_message

    def ins_merg_event(self, server_details, xml_string, server_user=None, user=None):
        if server_details.type == 'MISP':
            if user:
                pass
            else:
                user = self.event_controller.user_broker.get_by_id(self.get_user().identifier)
            self.misp_converter.api_key = server_details.user.api_key
            self.misp_converter.api_url = server_details.baseurl
            self.misp_converter.tag = server_details.name
            self.misp_converter.user = user
            merged_event = None
            try:
                event_uuid = self.misp_converter.get_uuid_from_event_xml(xml_string)
                try:
                    event = self.misp_converter.get_event_from_xml(xml_string, None)
                    self.logger.info('Received Event {0}'.format(event.uuid))
                    event.properties.is_validated = False
                    self.event_controller.insert_event(user, event, True, True)
                except ControllerIntegrityException as error:
                    local_event = self.event_controller.get_event_by_uuid(event_uuid)
                    event = self.misp_converter.get_event_from_xml(xml_string, local_event)
                    # merge event with existing event

                    if self.is_event_viewable(local_event, server_user):
                        event_permissions = self.get_event_user_permissions(event, user)
                        try:
                            merged_event = self.merger.merge_event(local_event, event, user, event_permissions)
                        except MergingException:
                            raise MISPAdapterException405()
                            # raise cherrypy.HTTPError(405)
                    else:
                        # TODO log the changes
                        self.logger.warning('user {0} tried to change event {1} but does not have the right to see it'.format(user.username, event.identifer))
                    if merged_event:
                        self.logger.info('Received Event {0} updates'.format(merged_event.uuid))
                        self.event_controller.update_event(user, merged_event, True, True)
                        event = merged_event
                    else:
                        self.logger.info('Received Event {0} did not need to update as it is up to date'.format(event.uuid))
                        # Log errors however
                        self.event_controller.event_broker.do_commit()

                return self.make_misp_xml(event, server_user)
            except BrokerException as error:
                self.logger.error('Received a MISP Event which caused errors')
                self.logger.error(error)
                # TODO Dump xml
                raise MISPAdapterException500()
                # raise cherrypy.HTTPError(500)
        else:
            raise MISPAdapterException409('Server is not a MISP Server')
            # raise cherrypy.HTTPError(409, 'Server is not a MISP Server')

    def pushed_event(self, xml_string, server_user):
        # instantiate misp converter
        user = self.get_user()
        try:
            server_details = self.server_broker.get_server_by_user_id(user.identifier)
            if server_details.type != 'MISP':
                raise cherrypy.HTTPError(409, 'Server is not a MISP Server')
            # check if it is a misp server else raise
            return self.ins_merg_event(server_details, xml_string, server_user)
        except BrokerException as error:
            self.logger.error(error)
            raise cherrypy.HTTPError(404)
        except MISPAdapterException405 as error:
            raise cherrypy.HTTPError(405)
        except MISPAdapterException409 as error:
            raise cherrypy.HTTPError(409)
        except MISPAdapterException500 as error:
            raise cherrypy.HTTPError(500)

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

            if local_event.last_publish_date >= datetime_from_string:
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
