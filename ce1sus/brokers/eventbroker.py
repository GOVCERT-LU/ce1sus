# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from c17Works.db.broker import BrokerBase, ValidationException, \
NothingFoundException, TooManyResultsFoundException, \
BrokerException
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, String, ForeignKey, Table, not_
from sqlalchemy.orm import relationship
from c17Works.db.session import BASE
from sqlalchemy.types import DateTime
from ce1sus.brokers.permissionbroker import User, Group
from c17Works.helpers.validator import ObjectValidator
from ce1sus.brokers.definitionbroker import AttributeDefinition, \
    ObjectDefinition, AttributeDefinitionBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from sqlalchemy.sql.expression import or_, and_
from ce1sus.brokers.valuebroker import ValueBroker
from ce1sus.web.helpers.handlers.base import HandlerBase

_REL_GROUPS_EVENTS = Table('Groups_has_Events', BASE.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)
_OBJECT_CROSSREFERENCE = Table('Obj_links_Obj', BASE.metadata,
    Column('object_id_to', Integer, ForeignKey('Objects.object_id')),
    Column('object_id_from', Integer, ForeignKey('Objects.object_id'))
)

class Attribute(BASE):
  """This is a container class for the ATTRIBUTES table."""
  def __init__(self):
    pass

  __tablename__ = "Attributes"
  identifier = Column('attribute_id', Integer, primary_key=True)
  def_attribute_id = Column(Integer,
                            ForeignKey('DEF_Attributes.def_attribute_id'))
  definition = relationship(AttributeDefinition,
              primaryjoin='AttributeDefinition.identifier==' +
              'Attribute.def_attribute_id', innerjoin=True)
  object_id = Column(Integer, ForeignKey('Objects.object_id'))
  object = relationship("Object",
                        primaryjoin='Object.identifier==Attribute.object_id')
  created = Column('created', DateTime)
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Attribute.creator_id==User.identifier")
  modifier_id = Column('modifier_id', Integer,
                            ForeignKey('Users.user_id'))
  modifier = relationship(User,
                          primaryjoin="Attribute.modifier_id==User.identifier")
  value_id = 0
  __value = None

  @property
  def key(self):
    """
    returns the name of the definition

    :returns: String
    """
    return getattr(self.definition, 'name')

  @property
  def value(self):
    """
    returns the actual value of the attribute

    :returns: Any
    """
    return self.__value

  @value.setter
  def value(self, value):
    """
    setter for the attribute value

    :param value: value to set
    :type value: Any
    """
    self.__value = value

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateDigits(self, 'def_attribute_id')
    ObjectValidator.validateDigits(self, 'object_id')
    ObjectValidator.validateDigits(self, 'creator_id')
    return ObjectValidator.isObjectValid(self)

class Event(BASE):
  """This is a container class for the EVENTS table."""
  def __init__(self):
    pass

  __tablename__ = "Events"
  identifier = Column('event_id', Integer, primary_key=True)
  title = Column('title', String)
  description = Column('description', String)
  first_seen = Column('first_seen', DateTime)
  last_seen = Column('last_seen', DateTime)
  modified = Column('modified', DateTime)
  tlp_level_id = Column('tlp_level_id', Integer)
  published = Column('published', Integer)
  status_id = Column('status_id', Integer)
  risk_id = Column('risk_id', Integer)
  analysis_status_id = Column('analysis_status_id', Integer)
  comments = relationship("Comment", backref="Events")
  groups = relationship(Group, secondary='Groups_has_Events', backref="events")
  objects = relationship('Object', backref="Events")
  created = Column('created', DateTime)
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Event.creator_id==User.identifier")
  modifier_id = Column('modifier_id', Integer,
                            ForeignKey('Users.user_id'))
  modifier = relationship(User,
                          primaryjoin="Event.modifier_id==User.identifier")
  __tlpObj = None

  def addObject(self, obj):
    """
    Add an object to this event

    :param obj: Obejct to be added
    :type obj: Obejct
    """
    errors = not obj.validate()
    if errors:
      raise ValidationException('Object to be added is invalid')
    function = getattr(self.objects, 'append')
    function(obj)

  @property
  def stauts(self):
    """
    returns the status

    :returns: String
    """
    return Status.getByID(self.status_id)

  @property
  def risk(self):
    """
    returns the status

    :returns: String
    """
    return Risk.getByID(self.status_id)

  @property
  def analysis(self):
    """
    returns the status

    :returns: String
    """
    return Analysis.getByID(self.status_id)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """
    if self.__tlpObj is None:
      self.__tlpObj = TLPLevel(self.tlp_level_id)
    return self.__tlpObj

  def addGroup(self, group):
    """
    Add a group to this event

    :param group: Group to be added
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be added is invalid')
    function = getattr(self.groups, 'append')
    function(group)

  def removeGroup(self, group):
    """
    Remove a group to this event

    :param group: Group to be removes
    :type group: Group
    """
    function = getattr(self.groups, 'remove')
    function(group)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'title', withSpaces=True, minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateDigits(self, 'tlp_level_id')
    ObjectValidator.validateDigits(self, 'status_id')
    ObjectValidator.validateDigits(self, 'published')
    ObjectValidator.validateDigits(self, 'creator_id')
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDateTime(self, 'modified')
    if not self.first_seen is None:
      ObjectValidator.validateDateTime(self, 'first_seen')
    if not self.last_seen is None:
      ObjectValidator.validateDateTime(self, 'last_seen')
    return ObjectValidator.isObjectValid(self)

class Comment(BASE):
  """This is a container class for the COMMENTS table."""
  def __init__(self):
    pass

  __tablename__ = "Comments"
  identifier = Column('comment_id', Integer, primary_key=True)
  # Event witch it belongs to
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event")
  comment = Column('comment', String)
  created = Column('created', DateTime)
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Comment.creator_id==User.identifier")
  modifier_id = Column('modifier_id', Integer,
                            ForeignKey('Users.user_id'))
  modifier = relationship(User,
                          primaryjoin="Comment.modifier_id==User.identifier")

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDigits(self, 'creator_id')
    ObjectValidator.validateDigits(self, 'event_id')
    ObjectValidator.validateAlNum(self,
                                  'comment',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)

class Object(BASE):
  """This is a container class for the OBJECTS table."""
  def __init__(self):
    pass

  __tablename__ = "Objects"
  identifier = Column('object_id', Integer, primary_key=True)
  attributes = relationship(Attribute, backref="objects")
  def_object_id = Column(Integer, ForeignKey('DEF_Objects.def_object_id'))
  definition = relationship(ObjectDefinition,
                            primaryjoin='ObjectDefinition.identifier' +
                            '==Object.def_object_id', innerjoin=True)
  objects = relationship("Object", secondary=_OBJECT_CROSSREFERENCE,
                         primaryjoin='Obj_links_Obj.c.object_id_to' +
                         '==Object.identifier',
                         secondaryjoin='Obj_links_Obj.c.object_id_from' +
                         '==Object.identifier',
                         backref="children")
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False, primaryjoin='Event.identifier' +
                       '==Object.event_id', innerjoin=True)
  created = Column('created', DateTime)
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Object.creator_id==User.identifier")
  def addAttribute(self, attribute):
    """
    Add an attribute to this event

    :param attribute: Attribute to be added
    :type attribute: Attribute
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be added is invalid')
    function = getattr(self.attributes, 'append')
    function(attribute)

  def removeAttribute(self, attribute):
    """
    remove this attribute

    :param attribute: Attribute to be removed
    :type attribute: Attribute
    """
    function = getattr(self.attributes, 'remove')
    function(attribute)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    for attribute in self.attributes:
      result = attribute.validate()
      if not result:
        return False
    function = getattr(self.definition, 'validate')
    if not function():
      return False
    ObjectValidator.validateDigits(self, 'creator_id')
    ObjectValidator.validateDigits(self, 'def_object_id')
    ObjectValidator.validateDigits(self, 'event_id')
    ObjectValidator.validateDateTime(self, 'created')
    return ObjectValidator.isObjectValid(self)

class CommentBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getAllByEventID(self, eventID):
    """
    Returns all the comments belonging to one event

    :param eventID: identifier of the event
    :type eventID: Integer

    :returns: List of Comments
    """
    try:

      result = self.session.query(Comment).filter(
                        Comment.event_id == eventID).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with event ID :{0}'.format(
                                                                  eventID))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return result

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Comment

class ObjectBroker(BrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attributeBroker = AttributeBroker(session)

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Object

  def removeByID(self, identifier, commit=True):
    """
    overrides BrokerBase.removeByID
    """
    try:
      obj = self.getByID(identifier)
      # remove attributes
      self.attributeBroker.removeAttributeList(obj.attributes, False)
      self.doCommit(False)
      BrokerBase.removeByID(self, obj.identifier, False)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
  def getByID(self, identifier):
    """
    overrides BrokerBase.getByID
    """
    obj = BrokerBase.getByID(self, identifier)
    # DO NEVER remove these lines else the object attributes will not
    # be displayed
    for attribute in obj.attributes:
      self.attributeBroker.getSetValues(attribute)
    return obj

class AttributeBroker(BrokerBase):
  """
  This broker handles all operations on attribute objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.valueBroker = ValueBroker(session)
    self.attributeDefinitionBroker = AttributeDefinitionBroker(session)

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Attribute

  def getSetValues(self, attribute):
    """sets the real values for the given attribute"""
    # execute select for the values
    try:
      value = self.valueBroker.getByAttribute(attribute)
      # value is an object i.e. StringValue and the value of the attribute is
      # the value of the value object
      # get handler
      handler = HandlerBase.getHandler(attribute.definition)
      # convert the attribute with the helper to a single line value
      attribute.value = handler.convertToAttributeValue(value)
      attribute.value_id = value.identifier
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found for attribute :{0}'.format(
                                                  attribute.definition.name))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
            'Too many results found for attribute :{0}'.format(
                                    attribute.definition.name))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getByID(self, identifier):
    """
    overrides BrokerBase.getByID
    """
    attribute = BrokerBase.getByID(self, identifier)
    self.getSetValues(attribute)
    return attribute

  def insert(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """
    # validation of the value of the attribute first
    # get the definition containing the definition how to validate an attribute
    definition = instance.definition
    ObjectValidator.validateRegex(instance,
                                  'value',
                                  definition.regex,
                                  'The value does not match {0}'.format(
                                                            definition.regex),
                                  False)
    errors = not instance.validate()
    if errors:
      raise ValidationException('Attribute to be inserted is invalid')
    try:
      BrokerBase.insert(self, instance, False)
      # insert value for value table
      self.doCommit(False)
      self.valueBroker.inserByAttribute(instance, False)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def update(self, instance, commit=True):
    """
    overrides BrokerBase.update
    """
    # validation of the value of the attribute first
    definition = instance.definiton
    ObjectValidator.validateRegex(instance,
                                  'value',
                                  definition.regex,
                                  'The value does not match {0}'.format(
                                                              definition.regex),
                                  False)
    errors = not instance.validate()
    if errors:
      raise ValidationException('Attribute to be updated is invalid')
    try:
      BrokerBase.update(self, instance, False)
      # updates the value of the value table
      self.doCommit(False)
      self.valueBroker.updateByAttribute(instance, False)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeByID(self, identifier, commit=True):
    try:
      attribute = self.getByID(identifier)
      self.valueBroker.removeByAttribute(attribute, False)
        # first remove values
      self.doCommit(False)
        # remove attribute
      BrokerBase.removeByID(self, identifier=attribute.identifier, commit=False)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeAttributeList(self, attributes, commit=True):
    """
      Removes all the attributes of the list

      :param attributes: List of attributes
      :type attributes: List of Attributes
    """
    try:
      for attribute in attributes:
        # remove attributes
        self.removeByID(attribute.identifier, False)
        self.doCommit(False)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

class EventBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attributeBroker = AttributeBroker(session)

  def getByID(self, identifier):
    """
    overrides BrokerBase.getByID
    """
    event = BrokerBase.getByID(self, identifier)
    # DO NEVER remove these lines else the object attributes will
    # not be displayed
    for obj in event.objects:
      for attribute in obj.attributes:
        self.attributeBroker.getSetValues(attribute)
    return event

  def insert(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Event to be inserted is invalid')
    try:
      BrokerBase.insert(self, instance, False)
      self.doCommit(False)
      # insert value for value table
      for obj in instance.objects:
        for attribute in obj.attributes:
          self.attributeBroker.insert(attribute, False)
      self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def update(self, instance, commit=True):
    """
    overrides BrokerBase.update
    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Event to be inserted is invalid')
    try:
      BrokerBase.update(self, instance, commit)
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

  def getAllForUser(self, user, limit=None, offset=None):
    """Returns all the tickets belonging to the groups"""
    if user.privileged:
      if limit is None or offset is None:
        limit = 200
        offset = 0
      return self.getAllLimited(limit, offset)
    else:
      groupIDs = list()
      for group  in user.groups:
        groupIDs.append(group.identifier)
      try:
        if (len(groupIDs) > 0):
          result = self.session.query(Event).join(User).filter(
                                        or_(
                                          User.identifier == user.identifier,
                                          and_(
                                            Group.identifier.in_(groupIDs),
                                            Event.published == 1)
                                          )
                                        ).order_by(
                        Event.created.desc()).limit(limit).offset(offset).all()
        else:
          result = self.session.query(Event).join(User).filter(
                                            User.identifier == user.identifier
                                            ).order_by(
                        Event.created.desc()).limit(limit).offset(offset).all()
      except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException('Nothing found')
      except sqlalchemy.exc.SQLAlchemyError as e:
        self.getLogger().fatal(e)
        self.session.rollback()
        raise BrokerException(e)
      return result

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

