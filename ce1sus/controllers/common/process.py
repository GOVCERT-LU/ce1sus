# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 8, 2014
"""

from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.common.processbroker import ProcessBroker
from ce1sus.db.classes.processitem import ProcessItem, ProcessType, ProcessStatus
from ce1sus.db.common.broker import BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ProcessController(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.process_broker = self.broker_factory(ProcessBroker)
    self.user_controller = UserController(config, session)

  def get_all_process_items(self):
    try:
      return self.process_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def create_new_process(self, type_, event_uuid, user, sync_server=None, commit=False):
    try:
      # if syncserver is none then it is for all the known servers
      user = self.user_controller.get_user_by_id(user.identifier)
      process_item = ProcessItem()
      if type_ in ProcessType.TYPES:
        process_item.type_ = type_
      else:
        raise ControllerException(u'Type "{0}" is not supported'.format(type_))
      process_item.status = ProcessStatus.SCHEDULED
      process_item.event_uuid = event_uuid
      if sync_server:
        process_item.server_details_id = sync_server.identifier
        process_item.server_details = sync_server
      self.set_simple_logging(process_item, user, True)

      self.process_broker.insert(process_item, commit)
      return process_item
    except BrokerException as error:
      raise ControllerException(error)

  def get_scheduled_process_items(self, user):
    # Get the scheduled items an mark them so that an other process will not take it
    try:
      scheduled_items = self.process_broker.get_scheduled_process_items()
      for item in scheduled_items:
        item.status = ProcessStatus.MARKED
        self.update_process_item(item, user, False)
      self.process_broker.do_commit(True)
      return scheduled_items
    except BrokerException as error:
      raise ControllerException(error)

  def get_process_item_by_uuid(self, uuid):
    try:
      return self.process_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_process_item_by_id(self, process_id):
    try:
      return self.process_broker.get_by_id(process_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_process_item_by_id(self, process_id):
    try:
      self.process_broker.remove_by_id(process_id)
    except BrokerException as error:
      raise ControllerException(error)

  def process_finished_success(self, process_item, user):
    # As the process finished successfully we remove it from the db
    # only keep the failed and scheduled ones
    self.logger.info(u'Process {0} terminated in success for user {1}'.format(process_item.identifier, user.identifier))
    self.remove_process_item_by_id(process_item.identifier)

  def process_finished_in_error(self, process_item, user):
    self.logger.critical(u'Process {0} terminated in failure for user {1}'.format(process_item.identifier, user.identifier))
    process_item.status = ProcessStatus.FAILED
    self.update_process_item(process_item, user)

  def process_cancelled(self, process_item, user):
    self.logger.critical(u'Process {0} cancelled by user {1}'.format(process_item.identifier, user.identifier))
    process_item.status = ProcessStatus.CANCELLED
    self.update_process_item(process_item, user)

  def process_restart(self, process_item, user):
    self.logger.critical(u'Process {0} restarted by user {1}'.format(process_item.identifier, user.identifier))
    process_item.status = ProcessStatus.SCHEDULED
    self.update_process_item(process_item, user)

  def process_remove(self, process_item, user):
    self.logger.critical(u'Process {0} removed by user {1}'.format(process_item.identifier, user.identifier))
    self.remove_process_item_by_id(process_item.identifier)

  def update_process_item(self, process_item, user, commit=True):
    user = self.user_controller.get_user_by_id(user.identifier)
    self.set_simple_logging(process_item, user, False)
    try:
      self.process_broker.update(process_item, False)
      self.process_broker.do_commit(True)
    except BrokerException as error:
      raise ControllerException(error)

  def process_task(self, process_item, user):
    process_item.status = ProcessStatus.PROCESSING
    self.update_process_item(process_item, user)
