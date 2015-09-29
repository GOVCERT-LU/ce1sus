# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 2, 2015
"""

import uuid

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.common.permissions import PermissionController
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.brokers.relationbroker import RelationBroker
from ce1sus.db.classes.internal.backend.relation import Relation
from ce1sus.db.common.broker import IntegrityException, BrokerException
from ce1sus.controllers.events.search import SearchController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RelationController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    super(RelationController, self).__init__(config, session)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.relation_broker = self.broker_factory(RelationBroker)
    self.permission_controller = self.controller_factory(PermissionController)
    self.search_controller = self.controller_factory(SearchController)

  def generate_bulk_attributes_relations(self, event, attributes, commit=False):
    # call partitions
    self.limited_generate_bulk_attributes(event, attributes, limit=10, commit=commit)

  def limited_generate_bulk_attributes(self, event, attributes, limit=1000, commit=False):
    # sport attributes by their definition
    partitions = dict()
    definitions = dict()
    values_attr = dict()
    for attribute in attributes:

      if attribute.definition.relation:
        attr_def_name = attribute.definition.name
        definitions[attr_def_name] = attribute.definition
        if not partitions.get(attr_def_name, None):
            # create partition list
          partitions[attr_def_name] = list()
          # create item list
          partitions[attr_def_name].append(list())
        if len(partitions[attr_def_name][len(partitions[attr_def_name]) - 1]) > limit:
          partitions[attr_def_name].append(list())
        partitions[attr_def_name][len(partitions[attr_def_name]) - 1].append(attribute.value)
        values_attr[attribute.value] = attribute

    # search in partitions
    for attr_def_name, partitions in partitions.iteritems():
      for search_items in partitions:
        definition = definitions.get(attr_def_name)
        self.find_relations_of_array(event, definition, search_items, values_attr, commit)
    self.relation_broker.do_commit(commit)

  def search_items(self, definition, unique_search_items):

    if definition.value_type and definition.value_type.name != 'None':
      #get all definitions related to this
      definitions = self.attr_def_broker.get_all_attribute_definitions_by_type(definition.value_type_id)
    else:
      definitions = [definition]
    
    result = list()
    for definition in definitions:
      result.extend(self.search_controller.search(unique_search_items, 'in', definition.name, definition.case_insensitive, True))
    return result

  def find_relations_of_array(self, event, definition, search_items, values_attr, commit=False):
    # collect relations
    unique_search_items = list(set(search_items))
    found_items = self.search_items(definition, unique_search_items)
    for found_item in found_items:
      # make insert foo
      if found_item.path.event_id != event.identifier:
        # make relation in both ways
        relation_entry = Relation()
        relation_entry.uuid = '{0}'.format(uuid.uuid4())
        relation_entry.event = event
        relation_entry.rel_event_id = found_item.path.event_id
        attribute = values_attr.get(found_item.value, None)
        if attribute:
          relation_entry.attribute = attribute
        else:
          continue
        relation_entry.rel_attribute_id = found_item.identifier
        try:
          self.relation_broker.insert(relation_entry, False)
        except IntegrityException:
          # do nothing if duplicate
          pass
    self.relation_broker.do_commit(commit)

  def get_related_events_for_event(self, event):
    try:
      return self.relation_broker.get_relations_by_event(event, unique_events=True)
    except BrokerException as error:
      raise ControllerException(error)

  def get_relations_for_event(self, event):
    try:
      return self.relation_broker.get_relations_by_event(event, unique_events=True)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_relations_for_event(self, event):
    try:
      return self.relation_broker.remove_relations_for_event(event)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_all_relations_by_definition_ids(self, id_list, commit=True):
    try:
      relations = self.relation_broker.get_all_rel_with_not_def_list(id_list)
      if relations:
        for relation in relations:
          self.relation_broker.remove_by_id(relation.identifier, False)
        self.relation_broker.do_commit(commit)
        return len(relations)
      else:
        return 0
    except BrokerException as error:
      raise ControllerException(error)

  def clear_relations_table(self):
    try:
      self.relation_broker.clear_relations_table()
    except BrokerException as error:
      raise ControllerException(error)
