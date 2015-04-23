# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 16, 2015
"""
from os.path import dirname, abspath

from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.brokers.permissions.group import GroupBroker
from ce1sus.db.classes.processitem import ProcessType
from ce1sus.db.common.broker import BrokerException
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.datumzait import DatumZait
from ce1sus.mappers.misp.mispce1sus import MispConverter, MispConverterException
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
    self.event_broker = self.user_controller.broker_factory(EventBroker)
    self.group_broker = self.user_controller.broker_factory(GroupBroker)
    self.mail_controller = MailController(config, directconnection)

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
    elif server_details.type == 'ce1sus':
      # TODO sceduling for ce1sus
      self.__push_ce1sus(item, event)
    else:
      raise SchedulerException('Server type {0} is unkown'.format(server_details.type))

  def __push_ce1sus(self, item, event):
    pass

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

  def __publish(self, item):
    try:
      event = self.event_broker.get_by_uuid(item.event_uuid)
      if item.server_details:
        # do the sync only for this server
        self.__publish_event(item, event)
      else:
        # it is to send emails
        self.__send_mails(event, item.type_)
      # set event as published
      event.last_publish_date = DatumZait.utcnow()
      self.event_broker.update(event, True)
      # remove item from queue
      self.process_controller.process_finished_success(item, self.user)
    except (ControllerException, BrokerException) as error:
      self.process_controller.process_finished_in_error(item, self.user)
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
    if type_ == ProcessType.PUBLISH:
      return self.mail_controller.get_publication_mail(event, user, group)
    elif type_ == ProcessType.PUBLISH_UPDATE:
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
      elif item.server_details.type == 'ce1sus':
        # TODO sceduling for ce1sus
        pass
      else:
        raise SchedulerException('Server type {0} is unkown'.format(item.server_details.type))
    else:
      # do the sync for all servers which are pull servers
      pass

  def __push(self, item):
    if item.server_details:
      # do the sync only for this server
      if item.server_details.type == 'MISP':
        event = self.event_broker.get_by_uuid(item.event_uuid)
        self.__push_misp(item, event)

      elif item.server_details.type == 'ce1sus':
        # TODO sceduling for ce1sus
        self.__push_ce1sus(item, event)
      else:
        raise SchedulerException('Server type {0} is unkown'.format(item.server_details.type))
    else:
      # do the sync for all servers which are push servers
      pass

  def process(self):
    # get all items
    items = self.process_controller.get_scheduled_process_items(self.user)
    for item in items:
      try:
        # decide type:
        self.process_controller.process_task(item, self.user)
        if item.type_ == ProcessType.PUBLISH or item.type_ == ProcessType.PUBLISH_UPDATE:
          self.__publish(item)
        elif item.type_ == ProcessType.PULL:
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

if __name__ == '__main__':
  basePath = dirname(abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  s = Scheduler(config)
  s.process()
