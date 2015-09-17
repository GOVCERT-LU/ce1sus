# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.controllers.common.common import CommonController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.common.broker import BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    super(AttributeController, self).__init__(config, session)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.common_controller = self.controller_factory(CommonController)
    self.relations_controller = self.controller_factory(RelationController)

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

  def update_attribute(self, attribute, cache_object, commit=True):
    # TODO: include handler
    try:
      self.update_set_base(attribute, cache_object)
      # TODO integrate handlersd
      self.attribute_broker.update(attribute)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_attribute(self, attribute, cache_object, commit=True):
    # TODO: include handler
    try:
      self.insert_set_base(attribute, cache_object)
      self.common_controller.remove_path(attribute.path, cache_object, False)
      self.attribute_broker.remove_by_id(attribute.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_attributes(self, attributes, cache_object, commit=True, mkrelations=True):
    # handle handler attributes
    try:
      # update parent
      if len(attributes) > 0:
        attribute = attributes[0]
        self.insert_set_base(attribute, cache_object)
      else:
        raise ControllerException('No attributes given to insert')


      self.relations_controller = self.controller_factory(RelationController)

      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relations_controller.generate_bulk_attributes_relations(attributes[0].path.event, attributes, False)


      # set owner
      for attribute in attributes:
        self.attribute_broker.insert(attribute, commit=False)

      self.attribute_broker.do_commit(commit)
      return attributes
    except BrokerException as error:
      raise ControllerException(error)
