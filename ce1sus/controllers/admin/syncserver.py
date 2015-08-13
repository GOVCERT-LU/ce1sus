# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.syncserverbroker import SyncServerBroker
from ce1sus.db.classes.internal.common import ServerType
from ce1sus.db.common.broker import BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SyncServerController(BaseController):

  def __init__(self, config, session=None):
    super(SyncServerController, self).__init__(config, session)
    self.sync_server_broker = self.broker_factory(SyncServerBroker)

  def get_all_servers(self):
    try:
      return self.sync_server_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_pull_servers(self):
    try:
      return self.sync_server_broker.get_all_pull_servers()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_push_servers(self):
    try:
      return self.sync_server_broker.get_all_push_servers()
    except BrokerException as error:
      raise ControllerException(error)

  def get_server_by_uuid(self, uuid):
    try:
      return self.sync_server_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_server(self, server, user):
    try:
      self.sync_server_broker.remove_by_id(server.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def update_server(self, server, commit=True):
    try:
      self.sync_server_broker.update(server, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_server(self, server, commit=True):
    try:
      self.sync_server_broker.insert(server, commit)

    except BrokerException as error:
      raise ControllerException(error)

  def get_all_types(self):
    values = ServerType.get_dictionary()
    return values
