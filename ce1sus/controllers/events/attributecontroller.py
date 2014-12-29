# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    BaseController.__init__(self, config)
    self.attribute_broker = self.broker_factory(AttributeBroker)

  def get_attribute_by_id(self, identifier):
    try:
      return self.attribute_broker.get_by_id(identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_attribute(self, attribute, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(attribute, user, user.group, False)
      self.attribute_broker.update(attribute)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_attribute(self, attribute, user, commit=True):
    try:
      self.attribute_broker.remove_by_id(attribute.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_attribute(self, attribute, user, commit=True):
    self.logger.debug('User {0} inserts a new attribute'.format(user.username))
    try:

      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(attribute, user, user.group, True)
      self.attribute_broker.insert(attribute, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.attribute_broker.do_commit(commit)
      return attribute, True
    except BrokerException as error:
      raise ControllerException(error)
