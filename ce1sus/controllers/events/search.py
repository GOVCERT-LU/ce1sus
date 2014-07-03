# -*- coding: utf-8 -*-

"""
module handing the search pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.controllers.base import Ce1susBaseController, ControllerException
from ce1sus.brokers.valuebroker import ValueBroker
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import ObjectDefinitionBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
import types
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.relationbroker import RelationBroker
from dagr.helpers.objects import get_class
from dagr.db.broker import BrokerException


# pylint:disable=R0903
class ResultItem(object):
  """
  Container Class for displaying the search results
  """
  # pylint:disable=R0913
  def __init__(self, identifier, event, attr_def, attribute):
    self.identifier = identifier
    self.event = event
    self.attr_def = attr_def
    self.attribute = attribute


class SearchController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.value_broker = self.broker_factory(ValueBroker)

  def get_cb_def_values_for_all(self):
    """
    Returns all the attribtue definitions formated for the combobox
    """
    try:
      return self.attr_def_broker.get_cb_values_for_all()
    except BrokerException as error:
      self._raise_exception(error)

  # pylint: disable=R0913
  def search_results(self, needle, definition_id, operant, user, cache=None):
    """
    handles the search and its results
    """
    try:
      result = list()
      if needle:
        # convert to the correct type
        if isinstance(needle, types.ListType):
          needle = needle[0]
        # GetClass
        needle = needle.strip()
        if len(needle) < 2:
          raise ControllerException('Needle has to be larger than 2')
        if definition_id == 'Any':
          definition = None
        else:
          definition = self.attr_def_broker.get_by_id(definition_id)
        found_values = self.attribute_broker.look_for_attribute_value(definition,
                                                                      needle,
                                                                      operant)
        # prepare displayItems
        if found_values:
          for found_value in found_values:
            if self._is_event_viewable_for_user(found_value.event, user, cache):

              obj = ResultItem(found_value.event_id,
                               found_value.event,
                               found_value.attribute.definition,
                               found_value.attribute)
              result.append(obj)
          return result
        else:
          return list()
      else:
        raise ControllerException('Please specify something before searching.')
    except BrokerException as error:
      self._raise_exception(error)

  def __remove_from_attrs(self, obj, object_attr_def_ids):
    self._get_logger().debug('Removing attributes')
    if object_attr_def_ids:
      to_be_removed = list()
      attributes = obj.attributes
      for attribute in attributes:
        if attribute.def_attribute_id not in object_attr_def_ids:
          to_be_removed.append(attribute)
      # remove items
      for attribute in to_be_removed:
        obj.attributes.remove(attribute)

  def __remove_form_objs(self, obj, obj_array, obj_def_id, object_attr_def_ids):
    self._get_logger().debug('Removing child objects and objects')
    self.__remove_from_attrs(obj, object_attr_def_ids)
    if obj.children:
      # go down
      for child in obj.children:
        self.__remove_form_objs(child, obj.children, obj_def_id, object_attr_def_ids)
    if not obj.children:
      # check if the object is of valid type else remove it
      if obj_def_id:
        if obj.def_object_id != obj_def_id:
          # remove object
          obj_array.remove(obj)

  def __remove_form_events(self, event, obj_def_id, object_attr_def_ids):
    self._get_logger().debug('Removing unneeded items')
    for obj in event.objects:
      self.__remove_form_objs(obj, event.objects, obj_def_id, object_attr_def_ids)

  def filtered_search_for_rest(self,
                              object_type,
                              object_attributes,
                              attribute_needles,
                              start_date,
                              end_date,
                              user,
                              cache=None,
                              limit=20,
                              offset=0):
    if not ((attribute_needles) or (object_type or object_attributes)):
      raise ControllerException('More parameters required for search')
    # TODO: include start_date, end_date
    try:
      values_to_look_for = dict()

      if attribute_needles:
        # collect all required definitions
        for item in attribute_needles:
          for definition_name, needle_op in item.iteritems():
            if definition_name == 'Any':
              definition = None
            else:
              definition = self.attr_def_broker.get_defintion_by_name(definition_name)
            # detect if there was an operator specified
            # check needle_op a dictionary
            if isinstance(needle_op, dict):
              # if dict take it appart
              needle = needle_op.get('value', None)
              if not needle:
                self._raise_exception(u'No needle was defined with this operator')
              operator = needle_op.get('operator', None)
              if not operator:
                self._raise_exception(u'No operator was defined for needle {0}'.format(needle))
            else:
              # else it is a sinlge value
              needle = needle_op
              operator = '=='
            values_to_look_for[needle] = definition

        # find all matching values
        matching_values = list()
        for needle, definition in values_to_look_for.iteritems():
          found_values = self.attribute_broker.look_for_attribute_value(definition,
                                                                      needle,
                                                                      operator)
          matching_values += found_values

      if object_type:
        # get definition
        obj_def = self.obj_def_broker.get_defintion_by_name(object_type)
        obj_def_id = obj_def.identifier
      else:
        obj_def_id = None

      object_attr_def_ids = list()
      if object_attributes:
        for definition_name in object_attributes:
          definition = self.attr_def_broker.get_defintion_by_name(definition_name)
          object_attr_def_ids.append(definition.identifier)

      # gather the found events
      events = list()
      seen_events = list()
      if attribute_needles:
        for item in matching_values:
          event = item.event
          self.__process_event(event, events, seen_events, user, cache, obj_def_id, object_attr_def_ids)
      else:
        matching_values = self.event_broker.get_all()
        for event in matching_values:
          self.__process_event(event, events, seen_events, user, cache, obj_def_id, object_attr_def_ids)
      return events
    except BrokerException as error:
      self._raise_exception(error)

  def __process_event(self, event, events, seen_events, user, cache, obj_def_id, object_attr_def_ids):
    # check if viewable
    if self._is_event_viewable_for_user(event, user, cache):
      # remove unwanted items from the event
      if event.identifier not in seen_events:
        self.__remove_form_events(event, obj_def_id, object_attr_def_ids)
        seen_events.append(event.identifier)
        events.append(event)
