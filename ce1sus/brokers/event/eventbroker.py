# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, ValidationException, \
NothingFoundException, TooManyResultsFoundException, \
BrokerException
import sqlalchemy.orm.exc
from ce1sus.brokers.permission.permissionclasses import Group
from sqlalchemy.sql.expression import or_, and_, not_
from datetime import datetime
from dagr.helpers.converters import ObjectConverter
from ce1sus.brokers.event.eventclasses import Event, Object
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
import uuid


class EventBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attributeBroker = AttributeBroker(session)
    self.objectBroker = ObjectBroker(session)

  def insert(self, instance, commit=True, validate=True):
    """
    overrides BrokerBase.insert
    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Event to be inserted is invalid')
    try:
      BrokerBase.insert(self, instance, False)
      # insert value for value table
      for obj in instance.objects:
        for attribute in obj.attributes:
          self.attributeBroker.insert(attribute, False, validate)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def update(self, instance, commit=True, validate=True):
    """
    overrides BrokerBase.update
    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Event to be inserted is invalid')
    try:
      BrokerBase.update(self, instance, commit, validate)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def updateLastSeen(self, event, user, commit=True):
    event.last_seen = datetime.now()
    event.modifier = user
    event.modifier_id = user.identifier
    self.update(event, commit)

  def getGroupsByEvent(self, identifier, belongIn=True):
    """
    Returns the groups of the given event

    Note: Password will be hashed inside this function

    :param identifier: identifier of the event
    :type identifier: Integer
    :param belongIn: If set returns all the groups of the event else
                     all the groups not belonging to the event
    :type belongIn: Boolean

    :returns: list of Groups

    :returns: Groups
    """
    try:
      groups = self.session.query(Group).join(Event.groups).filter(
                                          Event.identifier == identifier).all()
      if not belongIn:
        groupIDs = list()
        for group in groups:
          groupIDs.append(group.identifier)
        groups = self.session.query(Group).filter(not_(Group.identifier.in_(
                                                                    groupIDs)))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return groups

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Event

  def getAllLimited(self, limit, offset):
    """Returns only a subset of entries"""
    try:
      result = self.session.query(self.getBrokerClass()
                        ).order_by(
                        Event.created.desc()).limit(limit).offset(offset).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return result

  def __getAllAccordingToPermissions(self,
                                     user,
                                     limit,
                                     offset):
    if user.defaultGroup is None:
      # as the user has no main group it is impossible to see any thing
      result = list()
    else:
      tlpLVL = user.defaultGroup.tlpLvl
      mainGroupID = user.defaultGroup.identifier
      subGroupsIDs = list()
      for subgroup in user.defaultGroup.subgroups:
        subGroupsIDs.append(subgroup.identifier)
      try:
        if len(subGroupsIDs) > 0:
          result = self.session.query(Event).filter(
                                        or_(
                                          Event.creatorGroup_id == mainGroupID,
                                          and_(
                                            or_(
                                            Event.groups.identifier.in_(subGroupsIDs),
                                            Event.tlp_level_id >= tlpLVL
                                            ),
                                            Event.published == 1)
                                          )
                                        ).order_by(
                        Event.created.desc())
        else:
          result = self.session.query(Event).filter(
                                      or_(
                                        Event.creatorGroup_id == mainGroupID,
                                        and_(
                                            Event.tlp_level_id >= tlpLVL,
                                            Event.published == 1
                                            )
                                        )
                                      ).order_by(
                        Event.created.desc())
        if limit is None and offset is None:
          result = result.all()
        else:
          result = result.limit(limit).offset(offset).all()
      except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException('Nothing found')
      except sqlalchemy.exc.SQLAlchemyError as e:
        self.getLogger().fatal(e)
        self.session.rollback()
        raise BrokerException(e)
    return result

  def getAllForUser(self, user, limit=None, offset=None):
    """Returns all the events that the user can see"""
    if user.privileged:
      if limit is None or offset is None:
        limit = 200
        offset = 0
      return self.getAllLimited(limit, offset)
    else:
      return self.__getAllAccordingToPermissions(user,
                                                 limit,
                                                 offset)

  def addGroupToEvent(self, eventID, groupID, commit=True):
    """
    Add a group to an event

    :param eventID: Identifier of the event
    :type eventID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      event = self.session.query(Event).filter(Event.identifier ==
                                               eventID).one()
      event.addGroup(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or event not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeGroupFromEvent(self, eventID, groupID, commit=True):
    """
    removes a group to an event

    :param eventID: Identifier of the event
    :type eventID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      event = self.session.query(Event).filter(Event.identifier ==
                                               eventID).one()
      event.removeGroup(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  # pylint: disable=R0913
  def buildEvent(self,
                 identifier,
                 action,
                 status,
                 tlp_index,
                 description,
                 name,
                 published,
                 first_seen,
                 last_seen,
                 risk,
                 analysis,
                 user):
    """
    puts an event with the data together

    :param identifier: The identifier of the event,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String
    :param status: The identifier of the statuts
    :type status: Integer
    :param tlp_index: The identifier of the TLP level
    :type tlp_index: Integer
    :param description: The description
    :type description: String
    :param name: name or title of the event
    :type name: String
    :param published: the flag if the event is published
    :type published: Integer
    :param first_seen: DateTime of the fist occurrence of this event
    :type first_seen: DateTime
    :param last_seen: DateTime of the last occurrence of this event
    :type last_seen: DateTime
    :param risk: Id of the risk of this event
    :type risk: Integer
    :param analysis: Id of the analysis of this event
    :type analysis: Integer
    :param user: The user doing the action
    :type user: User

    :returns: Event
    """
    event = Event()
    if not action == 'insert':
      # dont want to change the original in case the user cancel!
      event = self.getByID(identifier)
      # right checks only if there is a change!!!!
    if not action == 'remove':
      event.title = name.strip()
      event.description = description.strip()
      ObjectConverter.setInteger(event, 'tlp_level_id', tlp_index)
      ObjectConverter.setInteger(event, 'status_id', status)
      ObjectConverter.setInteger(event, 'published', published)
      event.modified = datetime.now()
      event.modifier = user
      event.modifier_id = event.modifier.identifier
      event.uuid = unicode(uuid.uuid4())
      if first_seen:
        ObjectConverter.setDate(event, 'first_seen', first_seen)
      else:
        event.first_seen = datetime.now()
      if last_seen:
        ObjectConverter.setDate(event, 'last_seen', last_seen)
      else:
        event.last_seen = datetime.now()
      ObjectConverter.setInteger(event, 'analysis_status_id', analysis)
      ObjectConverter.setInteger(event, 'risk_id', risk)
      event.creatorGroup = user.defaultGroup
      event.creatorGroup_id = event.creatorGroup.identifier
      ObjectConverter.setInteger(event, 'creatorGroup_id', published)
      if action == 'insert':
        event.created = datetime.now()
        event.creator = user
        event.creator_id = event.creator.identifier
    return event

  def getEventByObjectID(self, objectID):
    """
    Returns the event hosting the object with the given id

    :param objectID: The identifier of an object
    :type objectID: Integer

    :returns: Event
    """
    try:
      obj = self.session.query(Object).filter(
                        Object.identifier == objectID).one()
      # if the object is a direct child of an event
      eventID = obj.parentObject_id
      if eventID is None:
        # if the object is a descendant of an object
        eventID = obj.event_id
      result = self.session.query(Event).filter(
                        Event.identifier == eventID).one()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                  objectID))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for ID :{0}'.format(objectID))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)
