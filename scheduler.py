# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 16, 2015
"""
from ce1sus.helpers.common.config import Configuration
from datetime import datetime
from os.path import dirname, abspath

from ce1sus.common.classes.cacheobject import CacheObject
from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.common.permissions import PermissionController
from ce1sus.controllers.common.process import ProcessController
from ce1sus.controllers.events.event import EventController
from ce1sus.db.brokers.permissions.group import GroupBroker
from ce1sus.db.classes.cstix.extensions.test_mechanism.generic_test_mechanism import GenericTestMechanism
from ce1sus.db.classes.internal.backend.processitem import ProcessType
from ce1sus.db.classes.internal.common import ServerType
from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.db.classes.internal.usrmgt.user import User
from ce1sus.db.common.broker import BrokerException
from ce1sus.db.common.session import SessionManager
from ce1sus.mappers.misp.mispce1sus import MispConverter
from ce1sus.views.web.adapters.ce1susadapter import Ce1susAdapterException, Ce1susAdapter, Ce1susAdapterNothingFoundException
from ce1sus.views.web.adapters.misp.misp import MISPAdapter, MISPAdapterException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SchedulerException(Exception):
  pass


class Scheduler(object):

  def __init__(self, config):
    self.config = config
    self.session_manager = SessionManager(config)
    directconnection = self.session_manager.connector.get_direct_session()
    self.process_controller = ProcessController(config, directconnection)
    self.server_controller = SyncServerController(config, directconnection)

    self.misp_converter = MispConverter(config)

    """
    self.dump = config.get('MISPMapper', 'dump', False)
    self.dump_location = config.get('MISPMapper', 'path', False)
    self.group_uuid = config.get('MISPMapper', 'transformergroup', None)
    self.misp_ctrl = MISPAdapter(config, directconnection)
    """



    user_uuid = config.get('ce1sus', 'maintenaceuseruuid', None)
    self.user_controller = UserController(config, directconnection)
    self.event_controller = EventController(config, directconnection)
    self.group_broker = self.user_controller.broker_factory(GroupBroker)
    self.mail_controller = MailController(config, directconnection)
    self.ce1sus_adapter = Ce1susAdapter(config, directconnection)
    self.permission_controller = PermissionController(config, directconnection)

    if None:
      raise SchedulerException('maintenaceuseruuid was not defined in config')
    try:
      self.user = self.user_controller.get_user_by_uuid(user_uuid)
    except ControllerNothingFoundException:
      raise SchedulerException('Cannot find maintenance user with uuid {0}'.format(user_uuid))
    except ControllerException as error:
      raise SchedulerException(error)



  def __push_ce1sus(self, item, event, dologin=True):
    try:
      self.ce1sus_adapter.server_details = item.server_details
      if dologin:
        self.ce1sus_adapter.login()
      rem_event = self.ce1sus_adapter.get_event_by_uuid(event.uuid, False, False)
      # check if server has the event already
      if rem_event:
        # update the event
        self.ce1sus_adapter.update_event(event, True, True)
      else:
        # insert the event
        self.ce1sus_adapter.insert_event(event, True, True)

    except Ce1susAdapterException as error:
      raise SchedulerException(error)

    try:
      if dologin:
        self.ce1sus_adapter.logout()
    except Ce1susAdapterException as error:
      raise SchedulerException(error)

  """
  def __push_misp(self, item, event):
    # set the parameters for misp
    self.misp_converter.api_key = item.server_details.user.api_key
    self.misp_converter.api_url = item.server_details.baseurl
    self.misp_converter.tag = item.server_details.name

    # cehck if event can be seen else ignore, normally should not happen
    if not self.misp_ctrl.is_event_viewable(event, item.server_details.user):
      # Ignore push
      return True
    # use the other function as it filters unwanted stuff out
    event_xml = self.misp_ctrl.make_misp_xml(event, item.server_details.user)

    try:
      self.misp_converter.push_event(event_xml)
      self.process_controller.process_finished_success(item, self.user)
    except MispConverterException as error:
      # TODO Log
      self.process_controller.process_finished_in_error(item, self.user)
      raise SchedulerException('Error during push of event {0} on server with url {1} with error {2}'.format(event.uuid, item.server_details.baseurl, error))
  """
  

  def __send_mails(self, event, type_, cache_object):
    # send mails only if plugin is enabled
    if self.mail_controller.mail_handler:
      try:
        seen_mails = list()

        # send mails for the users who wants them
        users = self.user_controller.get_all_notifiable_users()

        for user in users:
        # prevent double emails
          if user.email in seen_mails:
            continue
          else:
            # only send mails to users who can see the event!!!
            cache_object.user = user
            if self.permission_controller.is_instance_viewable(event, cache_object):
              if user.gpg_key:
                seen_mails.append(user.email)
                self.__send_mail(type_, event, user, None, True)
              else:
                # only send email when white
                if event.tlp_level_id >= 3:
                  seen_mails.append(user.email)
                  self.__send_mail(type_, event, user, None, False)

        # send the mails for the groups which want them
        groups = self.group_broker.get_all_notifiable_groups()
        cache_object.user = User()

        for group in groups:
          cache_object.user.group = group

          if group.email in seen_mails:
            continue
          else:
            if self.permission_controller.is_instance_viewable(event, cache_object):
                # only send mails to users who can see the event!!!
              seen_mails.append(group.email)
              if group.gpg_key:
                self.__send_mail(type_, event, None, group, True)
              else:
                # only send email when white
                if event.tlp_level_id >= 3:
                  self.__send_mail(type_, event, None, group, False)

      except (ControllerException, BrokerException) as error:
        raise SchedulerException(error)

  def __get_mail(self, event, type_, user, group):
    if type_ in [ProcessType.PUBLISH, ProcessType.REPUBLISH]:
      return self.mail_controller.get_publication_mail(event, user, group)
    elif type_ in [ProcessType.PUBLISH_UPDATE, ProcessType.REPUBLISH_UPDATE]:
      return self.mail_controller.get_publication_update_mail(event, user, group)
    elif type_ == ProcessType.PROPOSAL:
      return self.mail_controller.get_proposal_mail(event, user, group)
    else:
      raise SchedulerException(u'{0} is undefined'.format(type_))

  def __send_mail(self, type_, event, user, group, encrypt):
    # determine if it is an update
    mail = self.__get_mail(event, type_, user, group)
    mail.encrypt = encrypt
    # send mail
    self.mail_controller.send_mail(mail)

  def __pull(self, item):
    if item.server_details:
      # do the sync only for this server
      if item.server_details.type == ServerType.MISP:
        """
        # set the parameters for misp
        self.misp_converter.api_key = item.server_details.user.api_key
        self.misp_converter.api_url = item.server_details.baseurl
        self.misp_converter.tag = item.server_details.name
        # fetch one event from misp
        misp_event_xml = self.misp_converter.get_xml_event(item.event_uuid)
        # make insert/merge
        try:
          self.misp_ctrl.ins_merg_event(item.server_details, misp_event_xml, item.server_details.user, self.user)
          self.process_controller.process_finished_success(item, self.user)
        except MISPAdapterException as error:
          raise SchedulerException(error)

          # TODO dump xml or log it in browser
        """
        raise SchedulerException('Not implemented')

      elif item.server_details.type.lower() == ServerType.CELSUS:
        """
        self.ce1sus_adapter.server_details = item.server_details
        self.ce1sus_adapter.login()
        rem_json = self.ce1sus_adapter.get_event_by_uuid(item.event_uuid, True, True, True, True)

        # check if event exists
        try:
          event = self.event_controller.get_event_by_uuid(item.event_uuid)
          # merge the event fetched
          owner = is_event_owner(event, item.server_details.user)
          event = self.ce1sus_adapter.assembler.update_event(event, rem_json, item.server_details.user, owner, True)
          self.__insert_provenance_report(event, item.server_details)
          self.event_controller.update_event(self.user, event, True, True)
        except ControllerNothingFoundException:
          event = self.ce1sus_adapter.assembler.assemble_event(rem_json, item.server_details.user, True, True, False)
          event.properties.is_validated = False
          self.__insert_provenance_report(event, item.server_details)
          self.event_controller.insert_event(self.user, event, True, True)
        except ControllerException as error:
          self.ce1sus_adapter.logout()
          raise SchedulerException(error)
        self.ce1sus_adapter.logout()
        self.process_controller.process_finished_success(item, self.user)
        """
        raise SchedulerException('Not implemented')
      else:
        raise SchedulerException('Server type {0} is unkown'.format(item.server_details.type))
    else:
      # do the sync for all servers which are pull servers
      pass

  def __insert_provenance_report(self, event, server_details):
    report = Report()
    report.event = event
    self.ce1sus_adapter.set_extended_logging(report, server_details.user, server_details.user.group, True)

    reference = Reference()
    definition = self.misp_converter.reference_definitions_broker.get_by_uuid('dee2aa50-874e-4a92-9fd0-441171e76585')
    reference.definition = definition
    reference.value = '{0}/#/events/event/{1}'.format(server_details.baseurl, event.uuid)

    report.references.append(reference)
    event.reports.append(report)
    self.ce1sus_adapter.set_extended_logging(reference, server_details.user, server_details.user.group, True)

  def __push(self, item):
    if item.server_details:
      # do the sync only for this server
      if item.server_details.type == ServerType.MISP:
        event = self.event_controller.get_event_by_uuid(item.event_uuid)
        self.__push_misp(item, event)

      elif item.server_details.type == ServerType.CELSUS:
        self.ce1sus_adapter.server_details = item.server_details
        self.ce1sus_adapter.login()
        event = self.event_controller.get_event_by_uuid(item.event_uuid)
        try:
          try:
            rem_event = self.ce1sus_adapter.get_event_by_uuid(item.event_uuid, False, False, False, False)
            self.__insert_provenance_report(event, item.server_details)
            owner = is_event_owner(event, item.server_details.user)
            event = self.ce1sus_adapter.assembler.update_event(event, rem_event, item.server_details.user, owner, True)
            self.__insert_provenance_report(event, item.server_details)
            self.ce1sus_adapter.update_event(event, True, True)
          except Ce1susAdapterNothingFoundException:
            event.properties.validated = False
            self.__insert_provenance_report(event, item.server_details)
            self.ce1sus_adapter.insert_event(event, True, True)

          self.process_controller.process_finished_success(item, item.server_details.user)
        except (BrokerException, ControllerException, Ce1susAdapterException) as error:
          raise SchedulerException(error)
        finally:
          self.ce1sus_adapter.logout()
      else:
        raise SchedulerException('Server type {0} is unkown'.format(item.server_details.type))
    else:
      # do the sync for all servers which are push servers
      pass


  def __publish_event(self, item, event, cache_object):
    # server publishing
    if item.server_details:
      server_details = item.server_details
    else:
      raise SchedulerException('Server was not found defined')

    if server_details.type == ServerType.MISP:
      self.__push_misp(item, event)
    elif server_details.type == ServerType.CELSUS:
      self.__push_ce1sus(item, event)
    else:
      raise SchedulerException('Server type {0} is unknown'.format(server_details.type))



  def __publish(self, event_uuid, item_array):
    # publish the event with the given event id to the given process items -> less DB access
    event = self.event_controller.get_event_by_uuid(event_uuid)
    cache_object = CacheObject()
    item_publish = False
    for item in item_array:
      try:
        if item.server_details:
          # do the sync only for this server
          self.__publish_event(item, event, cache_object)
        else:
          # it is to send mails
          self.__send_mails(event, item.type_, cache_object)
        # set event as published only if it is the first publication
        if item.type_ in [ProcessType.PUBLISH, ProcessType.PUBLISH_UPDATE]:
          item_publish = True
        # remove item from queue
        self.process_controller.process_finished_success(item, self.user)
      except (ControllerException, BrokerException) as error:
        self.process_controller.process_finished_in_error(item, self.user)
    # only update the publish date once
    if item_publish:
      try:
        event.last_publish_date = datetime.utcnow()
        self.event_controller.update_event(self.user, event, True, True)
      except (ControllerException, BrokerException) as error:
        raise SchedulerException(error)



  def process(self):
    # get all items whch are not processed
    items = self.process_controller.get_scheduled_process_items(self.user)

    # sort out publications
    publications = list()

    remaining = list()

    for item in items:
      # mark for process
      self.process_controller.process_task(item, self.user)

      if item.type_ in [ProcessType.PUBLISH, ProcessType.PUBLISH_UPDATE, ProcessType.REPUBLISH, ProcessType.REPUBLISH_UPDATE]:
        publications.append(item)
      else:
        remaining.append(item)

    for item in remaining:
      try:
        if item.type_ == ProcessType.PULL:
          # self.__pull(item)
          raise SchedulerException('Not Implemented')
        elif item.type_ == ProcessType.PUSH:
          # self.__push(item)
          raise SchedulerException('Not Implemented')
        elif item.type_ == ProcessType.RELATIONS:
          raise SchedulerException('Not Implemented')
        elif item.type_ == ProcessType.PROPOSAL:
          # send out proposal mails
          self.__proposal(item)
      except SchedulerException:
        self.process_controller.process_finished_in_error(item, self.user)

    grouped_publications = dict()
    for item in publications:
      items = grouped_publications.get(item.event_uuid, None)
      if items is None:
        grouped_publications[item.event_uuid] = list()
      grouped_publications[item.event_uuid].append(item)

    for key, item_array in grouped_publications.iteritems():
      try:
        self.__publish(key, item_array)
      except SchedulerException:
        self.process_controller.process_finished_in_error(item, self.user)

if __name__ == '__main__':
  basePath = dirname(abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  s = Scheduler(config)
  s.process()
