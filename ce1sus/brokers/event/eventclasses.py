# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import ValidationException, BrokerException
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from dagr.db.session import BASE
from dagr.db.broker import DateTime
from ce1sus.brokers.permission.permissionclasses import User, Group, SubGroup
from dagr.helpers.validator.objectvalidator import ObjectValidator, \
                                                   FailedValidation
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition
from ce1sus.brokers.staticbroker import Status, Risk, Analysis, TLPLevel
from ce1sus.api.restclasses import RestEvent, RestObject, RestAttribute
from ce1sus.helpers.bitdecoder import BitValue
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition
from ce1sus.brokers.valuebroker import StringValue, DateValue, TextValue, \
                                       NumberValue
from ce1sus.brokers.definition.handlerdefinitionbroker import \
                                                       AttributeHandlerBroker
from dagr.db.session import SessionManager
from dagr.helpers.debug import Log
import importlib


_REL_GROUPS_EVENTS = Table('Groups_has_Events', BASE.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)
_REL_SUBGROUPS_EVENTS = Table('SubGroups_has_Events', BASE.metadata,
    Column('subgroup_id', Integer, ForeignKey('Subgroups.subgroup_id')),
    Column('event_id', Integer, ForeignKey('Events.event_id'))
)


# pylint: disable=R0902
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
  comments = relationship("Comment")
  groups = relationship(Group, secondary='Groups_has_Events', backref="events")
  maingroups = relationship(SubGroup,
                            secondary='SubGroups_has_Events')
  objects = relationship('Object', primaryjoin='Event.identifier' +
                       '==Object.event_id')
  created = Column('created', DateTime(timezone=True))
  modified = Column('modified', DateTime(timezone=True))
  # creators and modifiers will be gorups
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Event.creator_id==User.identifier")
  modifier_id = Column('modifier_id', Integer,
                            ForeignKey('Users.user_id'))
  modifier = relationship(User,
                          primaryjoin="Event.modifier_id==User.identifier")
  creatorGroup_id = Column('creatorGroup', Integer,
                            ForeignKey('Groups.group_id'))
  creatorGroup = relationship(Group,
                        primaryjoin="Event.creatorGroup_id==Group.identifier",
                        backref="createdEvents")
  __tlpObj = None
  uuid = Column('uuid', String)
  dbcode = Column('code', Integer)
  __bitCode = None

  @property
  def bitValue(self):
    if self.__bitCode is None:
        self.__bitCode = BitValue(self.dbcode, self)
    return self.__bitCode

  @bitValue.setter
  def bitValue(self, bitvalue):
    self.__bitCode = bitvalue

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
  def status(self):
    """
    returns the status

    :returns: String
    """
    return Status.getByID(self.status_id)

  @status.setter
  def setStatus(self, statusText):
    """
    returns the status

    :returns: String
    """
    self.status_id = Status.getByName(statusText)

  @property
  def risk(self):
    """
    returns the status

    :returns: String
    """
    return Risk.getByID(self.risk_id)

  @risk.setter
  def risk(self, riskText):
    """
    returns the status

    :returns: String
    """
    self.risk_id = Risk.getByName(riskText)

  @property
  def analysis(self):
    """
    returns the status

    :returns: String
    """
    return Analysis.getByID(self.analysis_status_id)

  @analysis.setter
  def analysis(self, text):
    """
    returns the status

    :returns: String
    """
    self.analysis_status_id = Analysis.getByName(text)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """
    if self.__tlpObj is None:
      self.__tlpObj = TLPLevel(self.tlp_level_id)
    return self.__tlpObj

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    pass

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
    ObjectValidator.validateDigits(self, 'risk_id')
    ObjectValidator.validateDigits(self, 'analysis_status_id')
    ObjectValidator.validateDigits(self, 'creator_id')
    ObjectValidator.validateDigits(self, 'modifier_id')
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDateTime(self, 'modified')
    if not self.first_seen is None:
      ObjectValidator.validateDateTime(self, 'first_seen')
    if not self.last_seen is None:
      ObjectValidator.validateDateTime(self, 'last_seen')
    if ((not self.first_seen is None and not self.last_seen is None) and
        not isinstance(self.first_seen, FailedValidation) and
        not isinstance(self.last_seen, FailedValidation)
        ):
      if self.first_seen > self.last_seen:
        setattr(self, 'first_seen',
                FailedValidation(self.first_seen,
                                 'First seen is after last seen.'))
        setattr(self, 'last_seen',
                FailedValidation(self.last_seen,
                                 'Last seen is before last seen.'))
    if self.first_seen is None and not self.last_seen is None:
        setattr(self, 'first_seen',
                FailedValidation(self.first_seen,
                                 'First seen cannot be empty when last seen is'
                                 + ' set.'))
        setattr(self, 'last_seen',
                FailedValidation(self.last_seen,
                                 'Last seen cannot be set when first seen is'
                                 + ' empty.'))
    return ObjectValidator.isObjectValid(self)

  def toRestObject(self, isOwner=False, full=True):
    result = RestEvent()
    result.tile = self.title
    result.description = self.description
    result.first_seen = self.first_seen
    result.last_seen = self.last_seen
    result.tlp = self.tlp
    result.risk = self.risk
    result.analysis = self.analysis
    result.uuid = self.uuid

    result.objects = list()
    if full:
      for obj in self.objects:
        # share only the objects which are shareable or are owned by the user
        if (obj.bitValue.isSharable and obj.bitValue.isValidated) or isOwner:
          result.objects.append(obj.toRestObject(isOwner))
    result.comments = list()
    if self.bitValue.isSharable:
      result.share = 1
    else:
      result.share = 0
    return result


# pylint: disable=R0903
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
    ObjectValidator.validateDigits(self, 'modifier_id')
    ObjectValidator.validateDigits(self, 'event_id')
    ObjectValidator.validateAlNum(self,
                                  'comment',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDateTime(self, 'modified')
    return ObjectValidator.isObjectValid(self)


class Object(BASE):
  """This is a container class for the OBJECTS table."""
  def __init__(self):
    pass

  __tablename__ = "Objects"
  identifier = Column('object_id', Integer, primary_key=True)
  attributes = relationship('Attribute')
  def_object_id = Column(Integer, ForeignKey('DEF_Objects.def_object_id'))
  definition = relationship(ObjectDefinition,
                            primaryjoin='ObjectDefinition.identifier' +
                            '==Object.def_object_id', lazy='joined')

  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False, primaryjoin='Event.identifier' +
                       '==Object.event_id')
  created = Column('created', DateTime)
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Object.creator_id==User.identifier")
  parentObject_id = Column('parentObject', Integer,
                            ForeignKey('Objects.object_id'))
  parentObject = relationship('Object',
                      primaryjoin="Object.parentObject_id==Object.identifier")

  parentEvent_id = Column('parentEvent', Integer, ForeignKey('Events.event_id'))
  parentEvent = relationship("Event",
                             uselist=False,
                             primaryjoin='Event.identifier' +
                             '==Object.parentEvent_id')
  children = relationship("Object", primaryjoin='Object.identifier' +
                         '==Object.parentObject_id')
  dbcode = Column('code', Integer)
  __bitCode = None

  @property
  def bitValue(self):
    if self.__bitCode is None:
        self.__bitCode = BitValue(self.dbcode, self)
    return self.__bitCode

  @bitValue.setter
  def bitValue(self, bitvalue):
    self.__bitCode = bitvalue
    self.dbcode = bitvalue.bitCode

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
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDigits(self, 'def_object_id')
    if not self.parentObject_id is None:
      ObjectValidator.validateDigits(self, 'parentObject_id')
    if not self.event_id is None:
      ObjectValidator.validateDigits(self, 'event_id')
    ObjectValidator.validateDateTime(self, 'created')
    return ObjectValidator.isObjectValid(self)

  def toRestObject(self, isOwner=False, full=True):
    result = RestObject()
    result.parentObject_id = self.parentObject_id
    result.parentEvent_id = self.parentEvent_id
    result.definition = self.definition.toRestObject()

    result.attributes = list()
    if full:
      for attribute in self.attributes:
        if (attribute.bitValue.isSharable and
                                      attribute.bitValue.isValidated) or isOwner:
          result.attributes.append(attribute.toRestObject(isOwner))
    result.children = list()
    if full:
      for obj in self.children:
        if (obj.bitValue.isSharable and obj.bitValue.isValidated) or isOwner:
          result.children.append(obj.toRestObject(isOwner))
    if self.bitValue.isSharable:
      result.share = 1
    else:
      result.share = 0
    return result


class Attribute(BASE):
  """This is a container class for the ATTRIBUTES table."""

  __tablename__ = "Attributes"
  identifier = Column('attribute_id', Integer, primary_key=True)
  def_attribute_id = Column(Integer,
                            ForeignKey('DEF_Attributes.def_attribute_id'))
  definition = relationship(AttributeDefinition,
              primaryjoin='AttributeDefinition.identifier==' +
              'Attribute.def_attribute_id', lazy='joined')
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
  ioc = Column('ioc', Integer)
  # valuerelations
  stringValue = relationship(StringValue,
                  primaryjoin="Attribute.identifier==StringValue.attribute_id",
                  lazy='joined', uselist=False,)
  dateValue = relationship(DateValue,
                  primaryjoin="Attribute.identifier==DateValue.attribute_id",
                  lazy='joined', uselist=False)
  textValue = relationship(TextValue,
                  primaryjoin="Attribute.identifier==TextValue.attribute_id",
                  lazy='joined', uselist=False)
  numberValue = relationship(NumberValue,
                  primaryjoin="Attribute.identifier==NumberValue.attribute_id",
                  lazy='joined', uselist=False)

  __value_id = None
  __value = None
  __valueObject = None
  dbcode = Column('code', Integer)
  __bitCode = None

  @property
  def bitValue(self):
    if self.__bitCode is None:
        self.__bitCode = BitValue(self.dbcode, self)
    return self.__bitCode

  @bitValue.setter
  def bitValue(self, bitvalue):
    self.__bitCode = bitvalue

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
    if self.__value is None:

      if not self.stringValue  is None:
        value = self.stringValue
      elif not self.dateValue  is None:
        value = self.dateValue
      elif not self.textValue is None:
        value = self.textValue
      elif not self.numberValue is None:
        value = self.numberValue

      try:
        sessionMangager = SessionManager.getInstance()
        handlerBroker = sessionMangager.brokerFactory(AttributeHandlerBroker)
        handler = handlerBroker.getHandler(self.definition)
        # Format the value if needed
        self.__value = handler.convertToAttributeValue(value)
      except BrokerException as e:
        Log.getLogger(self.__class__.__name__).error(e)
        self.__value = value.value

    return self.__value

  @value.setter
  def value(self, value):
    """
    setter for the attribute value

    :param value: value to set
    :type value: Any
    """
    """
    # attribute instance to attribute
    if self.definition:
      # instantiate class
      className = self.definition.className
      module = importlib.import_module('ce1sus.brokers.valuebroker')
      instance = getattr(module, className)()
      instance.value = value
      # set evetID
      eventID = self.object.event_id
      if eventID is None:
        eventID = self.object.parentEvent_id
      instance.event_id = eventID

      if className == 'StringValue':
        self.stringValue = instance
      elif className == 'DateValue':
        self.dateValue = instance
      elif className == 'TextValue':
        self.textValue = instance
      elif className == 'NumberValue':
        self.numberValue = instance

      self.__value = None
    else:
    """
    self.__value = value

  @property
  def isIOC(self):
    if self.ioc == 1:
      return 'Yes'
    else:
      return 'No'

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateDigits(self, 'def_attribute_id')
    ObjectValidator.validateDigits(self, 'object_id')
    ObjectValidator.validateDigits(self, 'creator_id')
    ObjectValidator.validateDigits(self, 'modifier_id')
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDateTime(self, 'modified')
    return ObjectValidator.isObjectValid(self)

  def toRestObject(self, isOwner=False):
    result = RestAttribute()
    result.definition = self.definition.toRestObject()
    result.value = self.value
    result.ioc = self.ioc
    if self.bitValue.isSharable:
      result.share = 1
    else:
      result.share = 0
    return result
