# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from dagr.db.broker import ValidationException
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from dagr.db.session import BASE
from dagr.db.broker import DateTime
from ce1sus.brokers.permission.permissionclasses import User, Group, SubGroup
from dagr.helpers.validator.objectvalidator import ObjectValidator, \
                                                   FailedValidation
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition
from ce1sus.brokers.staticbroker import Status, Risk, Analysis, TLPLevel
from ce1sus.helpers.bitdecoder import BitValue
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition
from ce1sus.brokers.valuebroker import StringValue, DateValue, TextValue, \
                                       NumberValue
from dagr.helpers.objects import get_class


_REL_GROUPS_EVENTS = Table('Groups_has_Events', getattr(BASE, 'metadata'),
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)
_REL_SUBGROUPS_EVENTS = Table('SubGroups_has_Events', getattr(BASE, 'metadata'),
    Column('subgroup_id', Integer, ForeignKey('Subgroups.subgroup_id')),
    Column('event_id', Integer, ForeignKey('Events.event_id'))
)


# pylint: disable=R0902,W0232
class Event(BASE):
  """This is a container class for the EVENTS table."""

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
  maingroups = relationship(Group, secondary='Groups_has_Events', backref="events")
  subgroups = relationship(SubGroup,
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
  creator_group_id = Column('creatorGroup', Integer,
                            ForeignKey('Groups.group_id'))
  creator_group = relationship(Group,
                        primaryjoin="Event.creator_group_id==Group.identifier",
                        backref="created_events")
  __tlp_obj = None
  uuid = Column('uuid', String)
  dbcode = Column('code', Integer)
  __bit_code = None
  last_publish_date = Column('last_publish_date', DateTime(timezone=True))

  @property
  def bit_value(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = BitValue('0', self)
      else:
        self.__bit_code = BitValue(self.dbcode, self)
    return self.__bit_code

  @bit_value.setter
  def bit_value(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

  def add_dbject(self, obj):
    """
    Add an object to this event

    :param obj: Obejct to be added
    :type obj: Obejct
    """
    errors = not obj.validate()
    if errors:
      raise ValidationException('Invalid Object:' + ValidationException(ObjectValidator.getFirstValidationError(obj)))
    function = getattr(self.objects, 'append')
    function(obj)

  @property
  def status(self):
    """
    returns the status

    :returns: String
    """
    return Status.get_by_id(self.status_id)

  @status.setter
  def set_status(self, status_text):
    """
    returns the status

    :returns: String
    """
    self.status_id = Status.get_by_name(status_text)

  @property
  def risk(self):
    """
    returns the status

    :returns: String
    """
    return Risk.get_by_id(self.risk_id)

  @risk.setter
  def risk(self, risk_text):
    """
    returns the status

    :returns: String
    """
    self.risk_id = Risk.get_by_name(risk_text)

  @property
  def analysis(self):
    """
    returns the status

    :returns: String
    """
    return Analysis.get_by_id(self.analysis_status_id)

  @analysis.setter
  def analysis(self, text):
    """
    returns the status

    :returns: String
    """
    self.analysis_status_id = Analysis.get_by_name(text)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """
    if self.__tlp_obj is None:
      self.__tlp_obj = TLPLevel(self.tlp_level_id)
    return self.__tlp_obj

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    pass

  def add_group(self, group):
    """
    Add a group to this event

    :param group: Group to be added
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Invalid Group:' + ValidationException(ObjectValidator.getFirstValidationError(group)))
    function = getattr(self.maingroups, 'append')
    function(group)

  def remove_group_from_event(self, group):
    """
    Remove a group to this event

    :param group: Group to be removes
    :type group: Group
    """
    function = getattr(self.maingroups, 'remove')
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
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id', Integer,
                            ForeignKey('Users.user_id'))
  creator = relationship(User,
                         primaryjoin="Object.creator_id==User.identifier")
  parent_object_id = Column('parentObject', Integer,
                            ForeignKey('Objects.object_id'))
  parent_object = relationship('Object',
                      primaryjoin="Object.parent_object_id==Object.identifier")

  parent_event_id = Column('parentEvent', Integer, ForeignKey('Events.event_id'))
  parent_event = relationship("Event",
                             uselist=False,
                             primaryjoin='Event.identifier' +
                             '==Object.parent_event_id')
  children = relationship("Object", primaryjoin='Object.identifier' +
                         '==Object.parent_object_id')
  dbcode = Column('code', Integer)
  uuid = Column('uuid', String)
  __bit_code = None

  @property
  def shared(self):
    """
    Property shared if set it is sharable else not
    """
    if self.bit_value.is_shareable:
      return 0
    else:
      return 1

  @shared.setter
  def shared(self, value):
    """
    Property shared if set it is sharable else not
    """
    if value == 1:
      self.bit_value.is_shareable = True
    else:
      self.bit_value.is_shareable = False

  @property
  def bit_value(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = BitValue('0', self)
      else:
        self.__bit_code = BitValue(self.dbcode, self)
    return self.__bit_code

  @bit_value.setter
  def bit_value(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

  def add_attribute(self, attribute):
    """
    Add an attribute to this event

    :param attribute: Attribute to be added
    :type attribute: Attribute
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException(ValidationException(ObjectValidator.getFirstValidationError(attribute)))
    function = getattr(self.attributes, 'append')
    function(attribute)

  def remove_attribute(self, attribute):
    """
    remove this attribute

    :param attribute: Attribute to be removed
    :type attribute: Attribute
    """
    function = getattr(self.attributes, 'remove')
    function(attribute)

  def validate(self, ignore_attribtues=False):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    if not ignore_attribtues:
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
    if not self.parent_object_id is None:
      ObjectValidator.validateDigits(self, 'parent_object_id')
    if not self.event_id is None:
      ObjectValidator.validateDigits(self, 'event_id')
    ObjectValidator.validateDateTime(self, 'created')
    return ObjectValidator.isObjectValid(self)

  def get_parent_event(self):
    """
    Returns the parent event of an object
    """
    if self.event:
      return self.event
    else:
      return self.parent_event

  def get_parent_event_id(self):
    """
    Returns the parent event ID of an object
    """
    if self.event:
      return self.event_id
    else:
      return self.parent_event_id


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
  string_value = relationship(StringValue,
                  primaryjoin="Attribute.identifier==StringValue.attribute_id",
                  lazy='joined', uselist=False)
  date_value = relationship(DateValue,
                  primaryjoin="Attribute.identifier==DateValue.attribute_id",
                  lazy='joined', uselist=False)
  text_value = relationship(TextValue,
                  primaryjoin="Attribute.identifier==TextValue.attribute_id",
                  lazy='joined', uselist=False)
  number_value = relationship(NumberValue,
                  primaryjoin="Attribute.identifier==NumberValue.attribute_id",
                  lazy='joined', uselist=False)
  attr_parent_id = Column('parent_attr_id', ForeignKey('Attributes.attribute_id'))
  children = relationship('Attribute',
                          primaryjoin="Attribute.identifier==Attribute.attr_parent_id")
  __value_id = None
  internal_value = None
  __value_obj = None
  __handler_class = None
  dbcode = Column('code', Integer)
  __bit_code = None
  config = None

  @property
  def shared(self):
    """
    Property shared if set it is sharable else not
    """
    if self.bit_value.is_shareable:
      return 0
    else:
      return 1

  @shared.setter
  def shared(self, value):
    """
    Property shared if set it is sharable else not
    """
    if value == 1:
      self.bit_value.is_shareable = True
    else:
      self.bit_value.is_shareable = False

  @property
  def bit_value(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = BitValue('0', self)
      else:
        self.__bit_code = BitValue(self.dbcode, self)
    return self.__bit_code

  @bit_value.setter
  def bit_value(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

  @property
  def key(self):
    """
    returns the name of the definition

    :returns: String
    """
    return getattr(self.definition, 'name')

  def __get_value_obj(self):
    """
    Returns the value object of an attibute
    """
    if not self.string_value  is None:
      value = self.string_value
    elif not self.date_value  is None:
      value = self.date_value
    elif not self.text_value is None:
      value = self.text_value
    elif not self.number_value is None:
      value = self.number_value
    else:
      value = None
    return value

  def __get_value(self):
    """
    Returns the actual value of an attribtue
    """
    if self.__value_obj is None:
      self.__value_obj = self.__get_value_obj()
      if self.__value_obj:
        self.internal_value = self.__value_obj.value
    return self.internal_value

  @property
  def value_id(self):
    """
    Returns the ID of the value in its table
    """
    value = self.__get_value()
    if value is None:
      return None
    else:
      if self.__value_obj is None:
        return None
      else:
        return getattr(self.__value_obj, 'identifier')

  @property
  def plain_value(self):
    """
    Returns the plain value of an attribute as it is stored in the DB
    """
    value = self.__get_value()
    if value is None:
      raise Exception('Empty value')
    else:
      return value

  @property
  def gui_value(self):
    """
    Returns the value of an attribute under the format for the GUI
    """
    self.__get_value()
    handler_instance = self.__get_handler_instance()
    value = handler_instance.convert_to_gui_value(self)
    return value

  @property
  def value(self):
    """
    Alias for plain_value
    """
    return self.plain_value

  @value.setter
  def value(self, value):
    """
    Plain value setter, somehow :)
    """
    if self.definition:
      classname = getattr(self.definition, 'classname')
      value_instance = get_class('ce1sus.brokers.valuebroker', classname)()
      value_instance.attribute_id = self.identifier
      value_instance.attribute = self
      value_instance.value = value
      if self.object:
        value_instance.event = getattr(self.object, 'get_parent_event')()
      else:
        raise Exception('No object was specified')
      # set the value
      attr_name = classname.replace('V', '_v').lower()
      setattr(self, attr_name, value_instance)
    else:
      raise Exception('No definition was specified')

  def __get_handler_instance(self):
    """
    returns the actual value of the attribute and its handler

    :returns: Object, instance of HandlerBase
    """
    return getattr(self.definition, 'handler')

  def validate(self, full=True):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateDigits(self, 'def_attribute_id')
    # validate attribute value
    value_obj = self.__get_value_obj()
    ObjectValidator.validateRegex(value_obj,
                                  'value',
                                  getattr(self.definition, 'regex'),
                                  'The value does not match {0}'.format(getattr(self.definition, 'regex')),
                                  True)
    errors = not getattr(value_obj, 'validate')()
    if errors:
      return False

    if full:
      ObjectValidator.validateDigits(self, 'object_id')
      ObjectValidator.validateDigits(self, 'creator_id')
      ObjectValidator.validateDigits(self, 'modifier_id')
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDateTime(self, 'modified')
    return ObjectValidator.isObjectValid(self)
