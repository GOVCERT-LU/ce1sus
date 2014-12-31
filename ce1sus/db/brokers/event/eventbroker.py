# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_, and_, not_, distinct

from ce1sus.db.classes.event import Event, EventGroupPermission
from ce1sus.db.classes.group import Group
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class EventBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Event

  def get_event_user_permissions(self, event, user):
    try:
      return self.session.query(EventGroupPermission).filter(and_(Event.identifier == event.identifier,
                                                                  Group.identifier == user.group.identifier
                                                                  )
                                                             )
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group {0} was not associated to event {1}'.format(user.group.identifier, event.identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_limited(self, limit, offset):
    """Returns only a subset of entries"""
    try:
      # TODO add validation and published checks
      # result = self.session.query(self.get_broker_class()).filter(Event.dbcode.op('&')(4) == 4).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
      result = self.session.query(Event).filter(Event.dbcode.op('&')(1) == 1).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    return result

  def get_all_limited_for_user(self, limit, offset, user):
    """Returns only a subset of entries"""
    try:
      # TODO: events for user
      # TODO add validation and published checks
      # result = self.session.query(self.get_broker_class()).filter(Event.dbcode.op('&')(4) == 4).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
      result = self.session.query(Event).filter(and_(Event.dbcode.op('&')(1) == 1, user.group.identifier in Event.groups)).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    return result

  def get_total_events(self):
    try:
      # TODO add validation and published checks
      result = self.session.query(self.get_broker_class()).count()
      return result
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def get_total_events_for_user(self, user):
    try:
      # TODO add validation and published checks
      # TODO: total events for user
      result = self.session.query(self.get_broker_class()).count()
      return result
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def get_all_unvalidated_total(self):
    try:
      result = self.session.query(Event).filter(Event.dbcode.op('&')(4) != 4).count()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return result

  def get_all_unvalidated(self, limit=None, offset=None):
    """
    Returns all unvalidated events
    """
    try:
      result = self.session.query(Event).filter(Event.dbcode.op('&')(4) != 4).order_by(Event.created_at.desc()).limit(limit).offset(offset).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return result

  def get_group_by_id(self, identifier):
    try:
      result = self.session.query(EventGroupPermission).filter(EventGroupPermission.identifier == identifier).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return result

  def update_group_permission(self, event_group_permission, commit=True):
    try:
      self.update(event_group_permission, commit)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def insert_group_permission(self, event_group_permission, commit=True):
    try:
      self.insert(event_group_permission, commit)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_group_permission_by_id(self, identifier, commit=True):
    try:
      self.session.query(EventGroupPermission).filter(EventGroupPermission.identifier == identifier).delete(synchronize_session='fetch')
      self.do_commit(commit)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
