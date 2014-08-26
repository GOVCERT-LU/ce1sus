# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.session import BASE
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from dagr.db.broker import BrokerBase, IntegrityException, BrokerException
from ce1sus.brokers.valuebroker import ValueBroker
import sqlalchemy.orm.exc
from ce1sus.brokers.event.eventclasses import Attribute
from sqlalchemy import or_
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition
from sqlalchemy import not_


# pylint: disable=R0903,R0902,W0232
class EventRelation(BASE):
  """
  Container class for event relations
  """
  __tablename__ = 'EventRelations'
  identifier = Column('EventRelations_id', Integer, primary_key=True)
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False,
                       primaryjoin='Event.identifier==EventRelation.event_id')
  rel_event_id = Column(Integer, ForeignKey('Events.event_id'))
  rel_event = relationship("Event",
                           uselist=False,
                           primaryjoin='Event.identifier==EventRelation.rel_event_id',
                           lazy='joined')
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute",
                           uselist=False,
                           primaryjoin='Attribute.identifier==EventRelation.attribute_id')
  rel_attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  rel_attribute = relationship("Attribute",
                               uselist=False,
                               primaryjoin='Attribute.identifier==EventRelation.attribute_id',
                               lazy='joined')

  def validate(self):
    """
    Returns true if the object is valid
    """
    return self


class RelationBroker(BrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attribute_definition_broker = AttributeDefinitionBroker(session)

  def generate_attribute_relations(self, attribute, commit=False):
    """
    Generates the relations for the given attribe

    :param attribute:
    :type attribute: Attribute
    :param commit:
    :type commit: Boolean

    """
    if attribute.definition.relation == 1:
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
          relation_entry = EventRelation()
          relation_entry.event_id = event.identifier
          relation_entry.rel_event_id = relation.event_id
          relation_entry.attribute_id = attribute.identifier
          relation_entry.rel_attribute_id = relation.attribute_id
          try:
            self.insert(relation_entry, False)
          except IntegrityException:
            # do nothing if duplicate
            pass
      self.do_commit(commit)

  def limited_generate_bulk_attributes(self, event, attributes, limit=1000, commit=False):
    # sport attributes by their definition
    partitions = dict()
    classes = dict()
    values_attr_id = dict()
    for attribtue in attributes:
      classname = attribtue.definition.classname
      if attribtue.definition.relation == 1:
        classes[classname] = ValueBroker.get_class_by_string(classname)
        if not partitions.get(classname, None):
            # create partition list
            partitions[classname] = list()
            # create item list
            partitions[classname].append(list())
        if len(partitions[classname][len(partitions[classname]) - 1]) > limit:
          partitions[classname].append(list())
        partitions[classname][len(partitions[classname]) - 1].append(attribtue.plain_value)
        values_attr_id[attribtue.plain_value] = attribtue.identifier

    # search in partitions
    for classname, partitions in partitions.iteritems():
      for search_items in partitions:
        clazz = classes.get(classname)
        self.find_relations_of_array(event, clazz, search_items, values_attr_id, commit)
    self.do_commit(commit)

  def find_relations_of_array(self, event, clazz, search_items, values_attr_id, commit=False):
    # collect relations
    found_items = self.session.query(clazz).filter(clazz.value.in_(search_items)).all()
    for found_item in found_items:
      # make insert foo
      if found_item.event_id != event.identifier:
        # make relation in both ways
        relation_entry = EventRelation()
        relation_entry.event_id = event.identifier
        relation_entry.rel_event_id = found_item.event_id
        attribute_id = values_attr_id.get(found_item.attribute.plain_value, None)
        if attribute_id:
          relation_entry.attribute_id = attribute_id
        else:
          continue
        relation_entry.rel_attribute_id = found_item.attribute_id
        try:
          self.insert(relation_entry, False)
        except IntegrityException:
          # do nothing if duplicate
          pass
    self.do_commit(commit)

  def generate_bulk_attributes_relations(self, event, attributes, commit=False):
    # call partitions
    self.limited_generate_bulk_attributes(event, attributes, limit=10, commit=commit)

  def get_relations_by_event(self, event, unique_events=True):
    """
    Returns the relations for a given event

    :param event:
    :type event: Event
    :param unique_events:
    :type unique_event: Boolean

    :returns: List of EventRelations
    """
    try:
      if unique_events:
        querry = self.session.query(EventRelation).distinct(EventRelation.event_id,
                                                            EventRelation.rel_event_id
                                                            ).group_by(EventRelation.event_id,
                                                                       EventRelation.rel_event_id
                                                                       ).filter(or_(EventRelation.event_id == event.identifier,
                                                                                    EventRelation.rel_event_id == event.identifier)
                                                                                )
      else:
        querry = self.session.query(EventRelation).filter(or_(EventRelation.event_id == event.identifier,
                                                              EventRelation.rel_event_id == event.identifier)
                                                          )
      relations = querry.all()
      # convert to event -> relation
      results = list()
      seen_events = list()
      for relation in relations:
        match = EventRelation()
        # check if event-> rel_event
        if relation.event_id == event.identifier:
          match = relation
        else:
          # else flip data
          match.identifier = relation.identifier
          match.event_id = relation.rel_event_id
          match.event = relation.rel_event
          match.rel_event_id = relation.event_id
          match.rel_event = relation.event
          match.attribute_id = relation.rel_attribute_id
          match.attribute = relation.rel_attribute
          match.rel_attribute_id = relation.attribute_id
          match.rel_attribute = relation.attribute
        if unique_events:
          if relation.rel_event_id not in seen_events:
            results.append(match)
            seen_events.append(match.rel_event_id)
        else:
          results.append(match)
      return results
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def clear_relations_table(self):
    try:
      self.session.query(EventRelation).delete()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    # convert

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return EventRelation

  def __look_for_value_by_class(self, clazz, value, operand, bypass_validation=False):
    """
    Searches the tables for a value
    """
    if bypass_validation:
      code = 0
    else:
      code = 4
    try:
      if operand == '==':
        return self.session.query(clazz).join(clazz.attribute).filter(clazz.value == value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '<':
        return self.session.query(clazz).join(clazz.attribute).filter(clazz.value < value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '>':
        return self.session.query(clazz).join(clazz.attribute).filter(clazz.value > value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '<=':
        return self.session.query(clazz).join(clazz.attribute).filter(clazz.value <= value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '>=':
        return self.session.query(clazz).join(clazz.attribute).filter(clazz.value >= value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == 'like':
        return self.session.query(clazz).join(clazz.attribute).filter(clazz.value.like('%{0}%'.format(value)),
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  # pylint: disable=R0913
  def __look_for_value_by_attrib_id(self,
                                    clazz,
                                    value,
                                    attribute_definition_id,
                                    operand='==',
                                    bypass_validation=False):
    """
    Searches the tables for the value using an attribute definition id
    """
    # will return only valid ones
    if bypass_validation:
      code = 0
    else:
      code = 4
    try:
      if operand == '==':
        return self.session.query(clazz).join(clazz.attribute).filter(Attribute.def_attribute_id == attribute_definition_id,
                                                                      clazz.value == value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '<':
        return self.session.query(clazz).join(clazz.attribute).filter(Attribute.def_attribute_id == attribute_definition_id,
                                                                      clazz.value < value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '>':
        return self.session.query(clazz).join(clazz.attribute).filter(Attribute.def_attribute_id == attribute_definition_id,
                                                                      clazz.value > value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '<=':
        return self.session.query(clazz).join(clazz.attribute).filter(Attribute.def_attribute_id == attribute_definition_id,
                                                                      clazz.value <= value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == '>=':
        return self.session.query(clazz).join(clazz.attribute).filter(Attribute.def_attribute_id == attribute_definition_id,
                                                                      clazz.value >= value,
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
      if operand == 'like':
        return self.session.query(clazz).join(clazz.attribute).filter(Attribute.def_attribute_id == attribute_definition_id,
                                                                      clazz.value.like('%{0}%'.format(value)),
                                                                      Attribute.dbcode.op('&')(code) == code
                                                                      ).all()
    except ValueError:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def look_for_attribute_value(self, attribute_definition, value, operand='=='):
    """
    returns a list of matching values

    :param attribute_definition: attribute definition to use for the lookup
    :type attribute_definition: AttributeDefinition
    :param value: Value to look for
    :type value: String

    :returns: List of clazz
    """
    result = list()
    if attribute_definition is None:
      # search by tables!
      try:
        clazzes = ValueBroker.get_all_classes()
        for clazz in clazzes:
          result = result + self.__look_for_value_by_class(clazz, value, operand, False)

      except BrokerException:
        pass

    else:
      clazz = ValueBroker.get_class_by_attr_def(attribute_definition)
      result = self.__look_for_value_by_attrib_id(clazz,
                                                  value,
                                                  attribute_definition.identifier,
                                                  operand,
                                                  False)

    return result

  def get_all_rel_with_not_def_list(self, def_ids):
    try:

      relations = self.session.query(EventRelation).join(Attribute, EventRelation.attribute_id == Attribute.identifier).join(AttributeDefinition, Attribute.def_attribute_id == AttributeDefinition.identifier).filter(not_(AttributeDefinition.identifier.in_(def_ids))).all()
      if relations:
        return relations
      else:
        return list()
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
