# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.definitions.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.db.brokers.definitions.referencesbroker import ReferenceDefintionsBroker
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.brokers.event.reportbroker import ReferenceBroker
from ce1sus.db.brokers.event.searchbroker import SearchBroker
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.db.classes.report import Report, Reference
from ce1sus.db.common.broker import BrokerException
from ce1sus.views.web.api.version3.handlers.restbase import valid_uuid


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SearchController(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.attribute_definition_broker = self.broker_factory(AttributeDefinitionBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.search_broker = self.broker_factory(SearchBroker)
    self.reference_definition_broker = self.broker_factory(ReferenceDefintionsBroker)
    self.reference_broker = self.broker_factory(ReferenceBroker)

  def get_all_attributes(self):
    """
    Returns all the attribute definitions formated for the combobox
    """
    try:
      attributes = self.attribute_definition_broker.get_all()
      return attributes
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_references(self):
    try:
      references = self.reference_definition_broker.get_all()
      return references
    except BrokerException as error:
      raise ControllerException(error)

  def search(self, needle, operator, definition_id):

    needle = needle.strip()
    found_values = list()

    if len(needle) < 2:
      raise ControllerException('Needle has to be larger than 2')
    if definition_id is None:
      found_values = self.__look_for_any_value(needle, operator)
    elif definition_id == 'uuid':
      found_values = self.__look_for_uuids(needle, operator)
    elif definition_id == 'title':
      found_values = self.__look_for_title(needle, operator)
    elif definition_id == 'description':
      found_values = self.__look_for_description(needle, operator)
    else:
      if 'attribute' in definition_id:
        uuid = definition_id.replace('attribute:', '')
        if valid_uuid(uuid):
          definition = self.attribute_definition_broker.get_by_uuid(uuid)
          found_values = self.attribute_broker.look_for_attribute_value(definition,
                                                                        needle,
                                                                        operator)
        else:
          raise ControllerException(u'{0} is not a valid uuid'.format(uuid))
      elif 'reference' in definition_id:
        uuid = definition_id.replace('reference:', '')
        if valid_uuid(uuid):
          definition = self.reference_definition_broker.get_by_uuid(uuid)
          found_values = self.reference_broker.look_for_reference_value(definition,
                                                                        needle,
                                                                        operator)
        else:
          raise ControllerException(u'{0} is not a valid uuid'.format(uuid))
      else:
        raise ControllerException(u'{0} is not a valid definition identifier'.format(definition_id))

    return found_values

  def __look_for_any_value(self, needle, operator):
    found_values = self.attribute_broker.look_for_attribute_value(None, needle, operator)
    # Also look inside uuids
    found_values = found_values + self.__look_for_uuids(needle, operator)

    found_values = found_values + self.__look_for_title(needle, operator)

    found_values = found_values + self.__look_for_description(needle, operator)

    found_values = found_values + self.reference_broker.look_for_reference_value(None,
                                                                                 needle,
                                                                                 operator)

    return found_values

  def __look_for_uuids(self, value, operand):
    found_values = list()
    for clazz in [Object, Attribute, Event, Observable, ObservableComposition, Report, Reference]:
      result = self.search_broker.look_for_uuid_by_class(clazz, value, operand)
      found_values = found_values + result
    return found_values

  def __look_for_title(self, value, operand):
    found_values = list()
    for clazz in [Event, Observable, Report]:
      result = self.search_broker.look_for_title_by_class(clazz, value, operand)
      found_values = found_values + result
    return found_values

  def __look_for_description(self, value, operand):
    found_values = list()
    for clazz in [Event, Observable, Report]:
      result = self.search_broker.look_for_description_by_class(clazz, value, operand)
      found_values = found_values + result
    return found_values
