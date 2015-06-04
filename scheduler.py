# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 16, 2015
"""
from ce1sus.helpers.common.config import Configuration
from datetime import datetime
from os.path import dirname, abspath

from ce1sus.common.checks import is_event_owner, is_event_viewable_user, is_event_viewable_group
from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.controllers.events.event import EventController
from ce1sus.db.brokers.permissions.group import GroupBroker
from ce1sus.db.classes.processitem import ProcessType
from ce1sus.db.classes.report import Report, Reference
from ce1sus.db.common.broker import BrokerException
from ce1sus.db.common.session import SessionManager
from ce1sus.mappers.misp.mispce1sus import MispConverter, MispConverterException
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
    self.misp_converter = MispConverter(config, None, None, None, directconnection)
    dump = config.get('MISPAdapter', 'dump', False)
    file_loc = config.get('MISPAdapter', 'file', None)
    self.misp_converter.dump = dump
    self.misp_converter.file_location = file_loc
    self.misp_ctrl = MISPAdapter(config, directconnection)
    user_uuid = config.get('ce1sus', 'maintenaceuseruuid', None)
    self.user_controller = UserController(config, directconnection)
    self.event_controller = EventController(config, directconnection)
    self.group_broker = self.user_controller.broker_factory(GroupBroker)
    self.mail_controller = MailController(config, directconnection)
    self.ce1sus_adapter = Ce1susAdapter(config, directconnection)
    if None:
      raise SchedulerException('maintenaceuseruuid was not defined in config')
    try:
      self.user = self.user_controller.get_user_by_uuid(user_uuid)
    except ControllerNothingFoundException:
      raise SchedulerException('Cannot find maintenance user with uuid {0}'.format(user_uuid))
    except ControllerException as error:
      raise SchedulerException(error)

  def __publish_event(self, item, event):
    # server publishing
    if item.server_details:
      server_details = item.server_details
    else:
      raise SchedulerException('Server could not be defined')

    if server_details.type == 'MISP':
      self.__push_misp(item, event)
    elif server_details.type == 'Ce1sus':
      self.__push_ce1sus(item, event)
    else:
      raise SchedulerException('Server type {0} is unkown'.format(server_details.type))

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

  def __publish(self, event_uuid, item_array):
    event = self.event_controller.get_event_by_uuid(event_uuid)
    item_publish = False
    for item in item_array:
      try:
        if item.server_details:
                    # do the sync only for this server
          self.__publish_event(item, event)
        else:
          # it is to send emails
          self.__send_mails(event, item.type_)
        # set event as published only if it is the furst publication
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

  def __send_mails(self, event, type_):
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
            if is_event_viewable_user(event, user):
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
        for group in groups:
          if group.email in seen_mails:
            continue
          else:
            if is_event_viewable_group(event, group):
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
      if item.server_details.type == 'MISP':
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
      elif item.server_details.type.lower() == 'ce1sus':
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
        pass
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
      if item.server_details.type == 'MISP':
        event = self.event_controller.get_event_by_uuid(item.event_uuid)
        self.__push_misp(item, event)

      elif item.server_details.type == 'Ce1sus':
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

  def process(self):
    # get all items
    items = self.process_controller.get_scheduled_process_items(self.user)

    # sort out publications
    publications = list()
    remaining = list()
    for item in items:
      self.process_controller.process_task(item, self.user)
      if item.type_ in [ProcessType.PUBLISH, ProcessType.PUBLISH_UPDATE, ProcessType.REPUBLISH, ProcessType.REPUBLISH_UPDATE]:
        publications.append(item)
      else:
        remaining.append(item)

    for item in remaining:
      try:
        if item.type_ == ProcessType.PULL:
          self.__pull(item)
        elif item.type_ == ProcessType.PUSH:
          self.__push(item)
        elif item.type_ == ProcessType.RELATIONS:
          # this is only possible if it is a ce1sus internal server, hence server details = none
          if item.server_details:
            raise SchedulerException('For relations the server details have to be none')
          else:
            # TODO: make relations
            pass
        elif item.type_ == ProcessType.PROPOSAL:
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
