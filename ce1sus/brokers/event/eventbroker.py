# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException
import sqlalchemy.orm.exc
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup
from sqlalchemy.sql.expression import or_, and_, not_
from dagr.helpers.datumzait import DatumZait
from ce1sus.brokers.event.eventclasses import Event
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker


# pylint: disable=R0904
class EventBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attribute_broker = AttributeBroker(session)
    self.object_broker = ObjectBroker(session)

  def __event_groups(self, clazz, join_relation, identifier, belong_in=True):
    """
    Returns all the groups of the event
    """
    try:
        groups = self.session.query(clazz).join(join_relation).filter(Event.identifier == identifier).all()
        if not belong_in:
            group_ids = list()
            for group in groups:
                group_ids.append(group.identifier)
            groups = self.session.query(clazz).filter(not_(clazz.identifier.in_(group_ids)))

    except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException(u'Nothing found for ID: {0}', format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
        raise BrokerException(error)
    return groups

  def get_event_groups(self, identifier, belong_in=True):
    """
    Returns the groups of the given event

    Note: Password will be hashed inside this function

    :param identifier: identifier of the event
    :type identifier: Integer
    :param belong_in: If set returns all the groups of the event else
                     all the groups not belonging to the event
    :type belong_in: Boolean

    :returns: list of Groups

    :returns: Groups
    """
    return self.__event_groups(Group, Event.maingroups, identifier, belong_in)

  def get_event_subgroups(self, identifier, belong_in=True):
    """
    Returns the groups of the given event

    Note: Password will be hashed inside this function

    :param identifier: identifier of the event
    :type identifier: Integer
    :param belong_in: If set returns all the groups of the event else
                     all the groups not belonging to the event
    :type belong_in: Boolean

    :returns: list of Groups

    :returns: Groups
    """
    return self.__event_groups(SubGroup, Event.subgroups, identifier, belong_in)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Event

  def get_all_limited(self, limit, offset):
    """Returns only a subset of entries"""
    try:
      result = self.session.query(self.get_broker_class()
                        ).filter(Event.dbcode.op('&')(4) == 4).order_by(
                        Event.created.desc()).limit(limit).offset(offset).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return result

  def __get_all_according_permissions(self,
                                     user,
                                     limit,
                                     offset):
    """
    Returns all the events taking into account the users groups
    """
    if user.default_group is None:
      # as the user has no main group it is impossible to see any thing
      result = list()
    else:
      tlp_lvl = user.default_group.tlp_lvl
      main_group_id = user.default_group.identifier
      sub_group_ids = list()
      for subgroup in user.default_group.subgroups:
        sub_group_ids.append(subgroup.identifier)
      try:
        # prepare list of event matching the groups
        try:
          maingroups = self.session.query(Event.identifier).join(Event.maingroups).filter(
                                           Event.dbcode.op('&')(12) == 12,
                                           Group.identifier == main_group_id
                                    ).all()
        except sqlalchemy.orm.exc.NoResultFound:
          maingroups = list()

        if len(sub_group_ids) > 0:
          try:
            subgroups = self.session.query(Event.identifier).join(Event.subgroups).filter(
                                             Event.dbcode.op('&')(12) == 12,
                                             Group.identifier.in_(sub_group_ids)
                                      ).all()
          except sqlalchemy.orm.exc.NoResultFound:
            subgroups = list()
        else:
          subgroups = list()
        event_ids = list()
        for item in maingroups + subgroups:
          event_ids.append(item[0])
        result = self.session.query(Event).filter(
                                                    or_(
                                                        and_(
                                                           Event.dbcode.op('&')(4) == 4,
                                                           Event.creator_group_id == main_group_id
                                                        ),
                                                        and_(
                                                             or_(
                                                                   Event.identifier.in_(event_ids),
                                                                   Event.tlp_level_id >= tlp_lvl
                                                                 ),
                                                           Event.published == 1
                                                        )
                                                    )
                                                  )
        if limit is None and offset is None:
          result = result.order_by(Event.created.desc()).all()
        else:
          result = result.order_by(Event.created.desc()).limit(limit).offset(offset).all()
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
      result = self.session.query(Event).filter(
                                            Event.dbcode.op('&')(4) != 4
                                               ).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return result

  def get_all_for_user(self, user, limit=None, offset=None):
    """Returns all the events that the user can see"""
    if user.privileged:
      if limit is None or offset is None:
        limit = 200
        offset = 0
      return self.get_all_limited(limit, offset)
    else:
      return self.__get_all_according_permissions(user,
                                                 limit,
                                                 offset)

  def __modify_event_groups(self, event_id, group_id, commit=True, insert=True):
    """
    Modifies group events
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               group_id).one()
      event = self.session.query(Event).filter(Event.identifier ==
                                               event_id).one()
      if insert:
        event.add_group(group)
      else:
        event.remove_group_from_event(group)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Group or event not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def add_group_to_event(self, event_id, group_id, commit=True):
    """
    Add a group to an event

    :param event_id: Identifier of the event
    :type event_id: Integer
    :param group_id: Identifier of the group
    :type group_id: Integer
    """
    self.__modify_event_groups(event_id, group_id, commit, True)

  def remove_group_from_event(self, event_id, group_id, commit=True):
    """
    removes a group to an event

    :param event_id: Identifier of the event
    :type event_id: Integer
    :param group_id: Identifier of the group
    :type group_id: Integer
    """
    self.__modify_event_groups(event_id, group_id, commit, False)

  def __modify_event_subgroups(self, event_id, group_id, commit=True, insert=True):
    """
    Performs changes in the event's subgroups
    """
    try:
      group = self.session.query(SubGroup).filter(SubGroup.identifier ==
                                               group_id).one()
      event = self.session.query(Event).filter(Event.identifier ==
                                               event_id).one()
      if insert:
        event.subgroups.append(group)
      else:
        event.subgroups.remove(group)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Group or event not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def add_subgroup_to_event(self, event_id, group_id, commit=True):
    """
    Add a group to an event

    :param event_id: Identifier of the event
    :type event_id: Integer
    :param group_id: Identifier of the group
    :type group_id: Integer
    """
    self.__modify_event_subgroups(event_id, group_id, commit, True)

  def remove_subgroup_from_event(self, event_id, group_id, commit=True):
    """
    removes a group to an event

    :param event_id: Identifier of the event
    :type event_id: Integer
    :param group_id: Identifier of the group
    :type group_id: Integer
    """
    self.__modify_event_subgroups(event_id, group_id, commit, False)

  def get_by_uuid(self, identifier):
    """
    Returns the object by the given identifier

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param uuid: the uuid of the requested user object
    :type uuid: String

    :returns: Object
    """
    try:

      result = self.session.query(Event).filter(
                        Event.uuid == identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with uuid :{0}'.format(
                                                                  identifier))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for uuid :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def get_events(self, uuids, start_date, end_date, offset, limit, user):
    """
    returns all the event
    """
    query = self.session.query(Event)
    try:
      if uuids:
        query = query.filter(Event.uuid.in_(uuids))

      if start_date:
        query = query.filter(Event.created >= start_date)
      if end_date:
        query = query.filter(Event.created <= end_date)
      if user.default_group is None:
        # as the user has no main group it is impossible to see any thing
        return list()
      else:
        tlp_lvl = user.default_group.tlp_lvl
        main_group_id = user.default_group.identifier
        subgroups_ids = list()
        subgroups_ids.append(main_group_id)
        for subgroup in user.default_group.subgroups:
          subgroups_ids.append(subgroup.identifier)
      # Dont forget to consider the permission
      query.filter(or_(
                      Event.creator_group_id == main_group_id,
                      and_(
                        or_(
                          Event.tlp_level_id >= tlp_lvl,
                          Event.dbcode.op('&')(12) == 12
                        ),
                        Event.published == 1)
                      )
                  )
      query.filter()
      query = query.order_by(Event.created.desc())
      query = query.limit(limit).offset(offset)

      return query.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Search did not yield any results.')
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def update_event(self, user, event, commit=True):
    """
    updates an event

    If it is invalid the event is returned

    :param event:
    :type event: Event
    """
    event.modifier = user
    event.modified = DatumZait.utcnow()
    self.update(event, False)
    self.do_commit(commit)
