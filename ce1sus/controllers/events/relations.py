# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 2, 2015
"""

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.brokers.relationbroker import RelationBroker
from ce1sus.db.brokers.values import ValueBroker
from ce1sus.db.classes.relation import Relation
from ce1sus.db.common.broker import IntegrityException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RelationController(BaseController):
    """event controller handling all actions in the event section"""

    def __init__(self, config, session=None):
        BaseController.__init__(self, config, session)
        self.attribute_broker = self.broker_factory(AttributeBroker)
        self.relation_broker = self.broker_factory(RelationBroker)

    def generate_attribute_relations(self, attribute, commit=False):
        try:
            """
            Generates the relations for the given attribue
            :param attribute:
            :type attribute: Attribute
            :param commit:
            :type commit: Boolean
            """
            if attribute.definition.relation:
                clazz = ValueBroker.get_class_by_attr_def(attribute.definition)
                relations = self.__look_for_value_by_attrib_id(clazz,
                                                               attribute.plain_value,
                                                               attribute.definition.identifier,
                                                               '==',
                                                               True)
                event = attribute.object.event
                for relation in relations:

                    # make insert foo
                    if relation.event_id != event.identifier:
                        # make relation in both ways
                        relation_entry = Relation()
                        relation_entry.event_id = event.identifier
                        relation_entry.rel_event_id = relation.event_id
                        relation_entry.attribute_id = attribute.identifier
                        relation_entry.rel_attribute_id = relation.attribute_id
                        try:
                            self.relation_broker.insert(relation_entry, False)
                        except IntegrityException:
                            # do nothing if duplicate
                            pass
                self.relation_broker.do_commit(commit)
        except BrokerException as error:
            raise ControllerException(error)

    def generate_bulk_attributes_relations(self, event, attributes, commit=False):
        # call partitions
        self.limited_generate_bulk_attributes(event, attributes, limit=10, commit=commit)

    def limited_generate_bulk_attributes(self, event, attributes, limit=1000, commit=False):
        # sport attributes by their definition
        partitions = dict()
        classes = dict()
        values_attr = dict()
        for attribute in attributes:

            value_table = attribute.definition.value_table
            classname = '{0}Value'.format(value_table)

            if attribute.definition.relation:
                classes[classname] = ValueBroker.get_class_by_string(value_table)
                if not partitions.get(classname, None):
                        # create partition list
                    partitions[classname] = list()
                    # create item list
                    partitions[classname].append(list())
                if len(partitions[classname][len(partitions[classname]) - 1]) > limit:
                    partitions[classname].append(list())
                partitions[classname][len(partitions[classname]) - 1].append(attribute.value)
                values_attr[attribute.value] = attribute

        # search in partitions
        for classname, partitions in partitions.iteritems():
            for search_items in partitions:
                clazz = classes.get(classname)
                self.find_relations_of_array(event, clazz, search_items, values_attr, commit)
        self.relation_broker.do_commit(commit)

    def find_relations_of_array(self, event, clazz, search_items, values_attr, commit=False):
        # collect relations
        unique_search_items = list(set(search_items))
        found_items = self.attribute_broker.get_attriutes_by_class_and_values(clazz, unique_search_items)
        for found_item in found_items:
            # make insert foo
            if found_item.event_id != event.identifier:
                # make relation in both ways
                relation_entry = Relation()
                relation_entry.event = event
                relation_entry.rel_event_id = found_item.event_id
                attribute = values_attr.get(found_item.attribute.value, None)
                if attribute:
                    relation_entry.attribute = attribute
                else:
                    continue
                relation_entry.rel_attribute_id = found_item.attribute_id
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

    def make_object_attributes_flat(self, obj):
        result = list()
        if obj:
            for attribute in obj.attributes:
                result.append(attribute)
            for related_object in obj.related_objects:
                result.extend(self.make_object_attributes_flat(related_object.object))
        return result

    def __process_observable(self, observable):
        result = list()
        if observable.observable_composition:
            for child_observable in observable.observable_composition.observables:
                result.extend(self.__process_observable(child_observable))
        else:
            result.extend(self.make_object_attributes_flat(observable.object))
        return result

    def get_flat_attributes_for_event(self, event):
        # Make attributes flat
        flat_attriutes = list()

        if event.observables:
            for observable in event.observables:
                if observable.observable_composition:
                    for obs in observable.observable_composition.observables:
                        flat_attriutes.extend(self.__process_observable(obs))
                else:
                    flat_attriutes.extend(self.__process_observable(observable))
        if event.indicators:
            for indicator in event.indicators:
                if indicator.observables:
                    for observable in indicator.observables:
                        flat_attriutes.extend(self.__process_observable(observable))
        return flat_attriutes

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
