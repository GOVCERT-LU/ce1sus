# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 19, 2013
"""

from sqlalchemy import or_
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import not_

from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.db.classes.relation import Relation
from ce1sus.db.common.broker import BrokerBase, BrokerException, \
  IntegrityException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RelationBroker(BrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_relations_by_event(self, event, unique_events=True):
    """
    Returns the relations for a given event

    :param event:
    :type event: Event
    :param unique_events:
    :type unique_event: Boolean

    :returns: List of Relations
    """
    try:
      if unique_events:
        querry = self.session.query(Relation).distinct(Relation.event_id,
                                                       Relation.rel_event_id
                                                       ).group_by(Relation.event_id,
                                                                  Relation.rel_event_id
                                                                  ).filter(or_(Relation.event_id == event.identifier,
                                                                               Relation.rel_event_id == event.identifier)
                                                                           )
      else:
        querry = self.session.query(Relation).filter(or_(Relation.event_id == event.identifier,
                                                         Relation.rel_event_id == event.identifier)
                                                     )
      relations = querry.all()
      # convert to event -> relation
      results = list()
      seen_events = list()
      for relation in relations:
        match = Relation()
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
      self.session.query(Relation).delete()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def remove_relations_for_event(self, event):
    try:
      self.session.query(Relation).filter(or_(Relation.event_id == event.identifier, Relation.rel_event_id == event.identifier)).delete(synchronize_session='fetch')
    except sqlalchemy.exc.IntegrityError as error:
      self.session.rollback()
      raise IntegrityException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Relation

  def get_all_rel_with_not_def_list(self, def_ids):
    try:
      relations = self.session.query(Relation).join(Attribute, Relation.attribute_id == Attribute.identifier).join(AttributeDefinition, Attribute.definition_id == AttributeDefinition.identifier).filter(not_(AttributeDefinition.identifier.in_(def_ids))).all()
      if relations:
        return relations
      else:
        return list()
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
