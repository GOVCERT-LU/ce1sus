# -*- coding: utf-8 -*-

"""
module handing the search pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.valuebroker import ValueBroker
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from importlib import import_module
from ce1sus.brokers.event.attributebroker import AttributeBroker
import types
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.relationbroker import RelationBroker


class SearchControllerException(Exception):
  """
  Exception
  """
  pass


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
    self.attribute_definition_broker = self.broker_factory(AttributeDefinitionBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.event_broker = self.broker_factory(EventBroker)
    self.relation_broker = self.broker_factory(RelationBroker)

  def get_cb_def_values_for_all(self):
    """
    Returns all the attribtue definitions formated for the combobox
    """
    return self.attribute_definition_broker.get_cb_values_for_all()

  def search_results(self, needle, definition_id, operant, user, cache=None):
    result = list()
    if needle:
      # convert to the correct type
      if isinstance(needle, types.ListType):
        needle = needle[0]
      # GetClass
      needle = needle.strip()
      if len(needle) < 2:
        raise SearchControllerException('Needle has to be larger than 2')
      if definition_id == 'Any':
        definition = None
      else:
        definition = self.attribute_definition_broker.get_by_id(definition_id)
        classname = definition.classname
        module = import_module('.valuebroker', 'ce1sus.brokers')
        clazz = getattr(module, classname)
        needle = clazz.convert(needle)

      found_values = self.relation_broker.look_for_attribute_value(definition,
                                                                  needle,
                                                                  operant)
      # prepare displayItems
      for found_value in found_values:
        if self._is_event_viewable_for_user(found_value.event, user, cache):

          obj = ResultItem(found_value.event_id,
                           found_value.event,
                           found_value.attribute.definition,
                           found_value.attribute)
          result.append(obj)
      return result
