# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.common.broker import BrokerException, NothingFoundException, IntegrityException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.attribute_broker = self.broker_factory(AttributeBroker)

  def get_attribute_by_id(self, identifier):
    try:
      return self.attribute_broker.get_by_id(identifier)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_attribute_by_uuid(self, uuid):
    try:
      return self.attribute_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_attribute(self, attribute, user, commit=True):
    # TODO: include handler
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(attribute, user, user.group, False)
      # TODO integrate handlersd
      self.attribute_broker.update(attribute)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_attribute(self, attribute, user, commit=True):
    # TODO: include handler
    try:
      self.attribute_broker.remove_by_id(attribute.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_attributes(self, attributes, user, commit=True, owner=True):
    self.logger.debug('User {0} inserts a new attribute'.format(user.username))

    # handle handler attributes

    try:

      user = self.user_broker.get_by_id(user.identifier)
      # set owner
      for attribute in attributes:
        if owner:
          attribute.properties.is_validated = True
        else:
          attribute.properties.is_proposal = True
        self.set_extended_logging(attribute, user, user.group, True)
        self.attribute_broker.insert(attribute, commit=False)

      self.attribute_broker.do_commit(commit)
      return attributes
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an attribute with uuid "{1}" but the uuid already exists'.format(user.username, attribute.uuid))
      raise ControllerException(u'An attribute with uuid "{0}" already exists'.format(attribute.uuid))
    except BrokerException as error:
      raise ControllerException(error)
