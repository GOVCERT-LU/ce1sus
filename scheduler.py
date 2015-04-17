# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 16, 2015
"""
from os.path import dirname, abspath

from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.db.classes.processitem import ProcessType
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.common.config import Configuration
from ce1sus.views.web.adapters.misp.misp import MISPAdapter, MISPAdapterException
from ce1sus.views.web.adapters.misp.mispce1sus import MispConverter, MispConverterException
from ce1sus.controllers.admin.user import UserController
from ce1sus.db.brokers.event.eventbroker import EventBroker


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
    if None:
      raise SchedulerException('maintenaceuseruuid was not defined in config')
    try:
      self.user = self.user_controller.get_user_by_uuid(user_uuid)
    except ControllerNothingFoundException:
      raise SchedulerException('Cannot find maintenance user with uuid {0}'.format(user_uuid))
    except ControllerException as error:
      raise SchedulerException(error)

  def __publish(self, item):

    if item.server_details:
      # do the sync only for this server
      if item.server_details.type == 'MISP':
        pass
      elif item.server_details.type == 'ce1sus':
        # TODO sceduling for ce1sus
        pass
      else:
        raise SchedulerException('Server type {0} is unkown'.format(item.server_details.type))
    else:
      # do the push for all servers which are push servers and mail to the users/groups
      pass

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
          self.logger.error(error)
          self.process_controller.process_finished_in_error(item, self.user)
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
        # set the parameters for misp
        self.misp_converter.api_key = item.server_details.user.api_key
        self.misp_converter.api_url = item.server_details.baseurl
        self.misp_converter.tag = item.server_details.name

        event = self.event_broker.get_by_uuid(item.event_uuid)
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

      elif item.server_details.type == 'ce1sus':
        # TODO sceduling for ce1sus
        pass
      else:
        raise SchedulerException('Server type {0} is unkown'.format(item.server_details.type))
    else:
      # do the sync for all servers which are push servers
      pass

  def process(self):
    # get all items
    items = self.process_controller.get_all_process_items()
    for item in items:
      # decide type:
      self.process_controller.process_task(item, self.user)
      if item.type_ == ProcessType.PUBLISH:
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

if __name__ == '__main__':
  basePath = dirname(abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  s = Scheduler(config)
  s.process()
