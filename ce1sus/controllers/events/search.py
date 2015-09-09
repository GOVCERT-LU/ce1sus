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
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.db.common.broker import BrokerException, NothingFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SearchController(BaseController):

  def __init__(self, config, session=None):
    super(SearchController, self).__init__(config, session)
    self.attribute_definition_broker = self.broker_factory(AttributeDefinitionBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.search_broker = self.broker_factory(SearchBroker)
    self.reference_definition_broker = self.broker_factory(ReferenceDefintionsBroker)
    self.reference_broker = self.broker_factory(ReferenceBroker)

  SEARCHABLE_CLASSES = [Object,
                        Attribute,
                        Event,
                        Observable,
                        ObservableComposition,
                        Report,
                        Reference,
                        Indicator,
                        STIXHeader
                        ]
  
  SEARCHABLE_PROPERIES = ['title',
                          'uuid',
                          ]
  
  def get_all_attributes(self):
    try:
      return self.attribute_definition_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_references(self):
    try:
      return self.reference_definition_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)



  def search(self, needle, operator, property_name):

    needle = needle.strip()
    found_values = list()

    if len(needle) < 2:
      raise ControllerException('Needle has to be larger than 2')

    if property_name is None or property_name == 'Any':
      found_values = self.serach_for_any_value(needle, operator)
    elif property_name == 'description':
      found_values = self.__look_for_descriptions(needle, operator)
    else:
      found_values = list()
      found = False
      try:
        definition = self.attribute_definition_broker.get_defintion_by_name(property_name)
        res = self.search_broker.look_for_attribute_value(definition,
                                                          needle,
                                                          operator)
        if res:
          found_values.extend(res)
        found = True
      except NothingFoundException:
        #the definition is not defined here
        pass
      
      try:
        res = self.search_broker.look_for_reference_value(property_name,
                                                             needle,
                                                             operator)
        if res:
          found_values.extend(res)
        found = True
      except NothingFoundException:
        #the definition is not defined here
        pass

      if not found:
        # try looking for the corresponding property
        res = self.search_by_property(property_name, needle, operator)
        if res:
          found_values.extend(res)

    return found_values

  def search_by_property(self, property_name, needle, operator):
    found_values = list()
    for clazz in SearchController.SEARCHABLE_CLASSES:
      found_values.extend(self.search_broker.look_for_value_by_property_name(clazz, property_name, needle, operator))
    return found_values

  def serach_for_any_value(self, needle, operator):
    found_values = self.search_broker.look_for_attribute_value(None, needle, operator)
    # Also look inside uuids

    found_values = found_values + self.__look_for_descriptions(needle, operator)

    for clazz in SearchController.SEARCHABLE_CLASSES:
      found_values = found_values + self.search_broker.look_for_value_by_properties(clazz, SearchController.SEARCHABLE_PROPERIES, needle, operator)

    found_values = found_values + self.search_broker.look_for_reference_value(None,
                                                                              needle,
                                                                              operator)

    return found_values

  def __look_for_descriptions(self, value, operand):
    found_values = list()
    for clazz in SearchController.SEARCHABLE_CLASSES:
      result = self.search_broker.look_for_descriptions(clazz, value, operand)
      found_values = found_values + result
    return found_values
