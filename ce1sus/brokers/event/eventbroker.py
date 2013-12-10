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
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup
from sqlalchemy.sql.expression import or_, and_, not_
from datetime import datetime
from dagr.helpers.converters import ObjectConverter
from ce1sus.brokers.event.eventclasses import Event, Object, \
                                              ObjectAttributeRelation
from ce1sus.brokers.event.attributebroker import AttributeBroker, Attribute
from ce1sus.brokers.event.objectbroker import ObjectBroker
import uuid
from ce1sus.helpers.bitdecoder import BitValue
from dagr.helpers.string import cleanPostValue


# pylint: disable=R0904
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

  def getSubGroupsByEvent(self, identifier, belongIn=True):
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
      groups = self.session.query(SubGroup).join(Event.maingroups).filter(
                                          Event.identifier == identifier).all()
      if not belongIn:
        groupIDs = list()
        for group in groups:
          groupIDs.append(group.identifier)
        groups = self.session.query(SubGroup).filter(not_(
                                                      SubGroup.identifier.in_(
                                                                    groupIDs
                                                                             )
                                                          )
                                                     )
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
                        ).filter(Event.dbcode.op('&')(4) == 4).order_by(
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
                                            Event.groups.identifier.in_(
                                                                  subGroupsIDs
                                                                       ),
                                            Event.tlp_level_id >= tlpLVL,
                                            Event.dbcode.op('&')(12) == 12
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
                                            Event.published == 1,
                                            Event.dbcode.op('&')(12) == 12
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

  def getAllUnvalidated(self, limit=None, offset=None):
    try:
      result = self.session.query(Event).filter(
                                            Event.dbcode.op('&')(4) != 4
                                               ).all()
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

  def addSubGroupToEvent(self, eventID, groupID, commit=True):
    """
    Add a group to an event

    :param eventID: Identifier of the event
    :type eventID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(SubGroup).filter(SubGroup.identifier ==
                                               groupID).one()
      event = self.session.query(Event).filter(Event.identifier ==
                                               eventID).one()
      event.maingroups.append(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or event not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeSubGroupFromEvent(self, eventID, groupID, commit=True):
    """
    removes a group to an event

    :param eventID: Identifier of the event
    :type eventID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(SubGroup).filter(SubGroup.identifier ==
                                               groupID).one()
      event = self.session.query(Event).filter(Event.identifier ==
                                               eventID).one()
      event.maingroups.remove(group)
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
      event.title = cleanPostValue(name)
      event.description = cleanPostValue(description)
      if not event.description:
        event.description = 'no description'
      ObjectConverter.setInteger(event, 'tlp_level_id', tlp_index)
      ObjectConverter.setInteger(event, 'status_id', status)
      ObjectConverter.setInteger(event, 'published', published)
      event.modified = datetime.now()
      event.modifier = user
      event.modifier_id = event.modifier.identifier

      if first_seen:
        ObjectConverter.setDate(event, 'first_seen', first_seen)
      else:
        event.first_seen = datetime.now()
      if last_seen:
        ObjectConverter.setDate(event, 'last_seen', last_seen)
      else:
        event.last_seen = event.first_seen
      ObjectConverter.setInteger(event, 'analysis_status_id', analysis)
      ObjectConverter.setInteger(event, 'risk_id', risk)
      if action == 'insert':
        event.uuid = unicode(uuid.uuid4())
        event.creatorGroup = user.defaultGroup
        event.creatorGroup_id = event.creatorGroup.identifier
        event.groups = list()
        event.groups.append(user.defaultGroup)
        event.bitValue = BitValue('1000', event)
        event.created = datetime.now()
        event.creator = user
        event.creator_id = event.creator.identifier
    return event

  def getByUUID(self, identifier):
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
      raise NothingFoundException('Nothing found with uuid :{0}'.format(
                                                                  identifier))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for uuid :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

  def getRelatedEvents(self, event):
    try:
      # get All the attributes from for the event
      attributes = self.session.query(Attribute).join(Object,
                                                      Event).filter(
                                          Event.identifier == event.identifier
                                                      ).all()
      # get All ids
      attributeIDs = list()
      for attribute in attributes:
        attributeIDs.append(attribute.identifier)

      # getAll RelatedEvents
      result = self.session.query(Event).join(Object,
                                              ObjectAttributeRelation
                                              ).filter(
                    ObjectAttributeRelation.sameAttribute_id.in_(attributeIDs),
                    Event.dbcode.op('&')(12) == 12
                    ).all()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with for ids :{0}'.format(
                                                                 attributeIDs))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

  def getEvents(self, uuids, startDate, endDate, offset, limit):
    query = self.session.query(Event)
    try:
      if uuids:
        query = query.filter(Event.uuid.in_(uuids))

      if startDate:
        query = query.filter(Event.created >= startDate)
      query = query.filter(Event.created <= endDate)
      query = query.order_by(Event.created.desc())
      query = query.limit(limit).offset(offset)
      return query.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Search did not yield any results.')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

  def updateEvent(self, event, commit=True):
    event.modified = datetime.now()
    self.update(event, False)
    self.doCommit(commit)



