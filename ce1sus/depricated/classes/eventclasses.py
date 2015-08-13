# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

import dateutil.tz
import re
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

from ce1sus.db.classes.internal.common import Status, Risk, Analysis, TLP
from ce1sus.db.common.session import BaseClass
from ce1sus.depricated.brokers.basefoo import BASE
from ce1sus.depricated.classes.definitionclasses import OldObjectDefinition, OldAttributeDefinition
from ce1sus.depricated.classes.permissionclasses import OldGroup, OldSubGroup
from ce1sus.depricated.classes.valuesclasses import OldStringValue, OldDateValue, OldTextValue, OldNumberValue
from ce1sus.depricated.helpers.bitdecoder import BitValue
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import ValidationException, ObjectValidator, FailedValidation


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_GROUPS_EVENTS = Table('Groups_has_Events', getattr(BASE, 'metadata'),
                           Column('event_id', Integer, ForeignKey('Events.event_id')),
                           Column('group_id', Integer, ForeignKey('Groups.group_id'))
                           )
_REL_SUBGROUPS_EVENTS = Table('SubGroups_has_Events', getattr(BASE, 'metadata'),
                              Column('subgroup_id', Integer, ForeignKey('Subgroups.subgroup_id')),
                              Column('event_id', Integer, ForeignKey('Events.event_id'))
                              )


# pylint: disable=R0902,W0232
class OldEvent(BASE):
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
  comments = relationship("OldComment")
  maingroups = relationship(OldGroup,
                            secondary='Groups_has_Events')
  subgroups = relationship(OldSubGroup,
                           secondary='SubGroups_has_Events')
  objects = relationship('OldObject',
                         primaryjoin='and_(OldEvent.identifier==OldObject.event_id, OldObject.parent_object_id==None)')
  created = Column('created',
                   DateTime(timezone=True))
  modified = Column('modified',
                    DateTime(timezone=True))
  # creators and modifiers will be groups
  creator_id = Column('creator_id',
                      Integer,
                      ForeignKey('Users.user_id'))
  modifier_id = Column('modifier_id',
                       Integer,
                       ForeignKey('Users.user_id'))
  creator_group_id = Column('creatorGroup',
                            Integer,
                            ForeignKey('Groups.group_id'))
  __tlp_obj = None
  uuid = Column('uuid', String)
  dbcode = Column('code', Integer)
  __bit_code = None
  last_publish_date = Column('last_publish_date', DateTime(timezone=True))

  def to_dict(self):
    comments = list()
    for comment in self.comments:
      comments.append(comment.to_dict())
    maingroups = list()
    for maingroup in self.maingroups:
      maingroups.append(maingroup.to_dict())
    subgroups = list()
    for subgroup in self.subgroups:
      subgroups.append(subgroup.to_dict())
    objects = list()
    for obj in self.objects:
      objects.append(obj.to_dict())

    return {'identifier': BaseClass.convert_value(self.identifier),
            'created': BaseClass.convert_value(self.created),
            'analysis_status_id': BaseClass.convert_value(self.analysis_status_id),
            'creator_group_id': BaseClass.convert_value(self.creator_group_id),
            'creator_id': BaseClass.convert_value(self.creator_id),
            'modifier_id': BaseClass.convert_value(self.modifier_id),
            'dbcode': BaseClass.convert_value(self.dbcode),
            'description': BaseClass.convert_value(self.description),
            'title': BaseClass.convert_value(self.title),
            'first_seen': BaseClass.convert_value(self.first_seen),
            'last_seen': BaseClass.convert_value(self.last_seen),
            'modified': BaseClass.convert_value(self.modified),
            'tlp_level_id': BaseClass.convert_value(self.tlp_level_id),
            'published': BaseClass.convert_value(self.published),
            'status_id': BaseClass.convert_value(self.status_id),
            'risk_id': BaseClass.convert_value(self.risk_id),
            'analysis_status_id': BaseClass.convert_value(self.analysis_status_id),
            'comments': comments,
            'maingroups': maingroups,
            'subgroups': subgroups,
            'objects': objects,
            'uuid': BaseClass.convert_value(self.uuid),
            'last_publish_date': BaseClass.convert_value(self.last_publish_date)
            }

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
      raise ValidationException(u'Invalid Object:' + ValidationException(ObjectValidator.getFirstValidationError(obj)))
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
    self.status_id = Status.get_by_value(status_text)

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
    self.risk_id = Risk.get_by_value(risk_text)

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
    self.analysis_status_id = Analysis.get_by_value(text)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """
    if self.__tlp_obj is None:
      self.__tlp_obj = TLP(self.tlp_level_id)
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
      raise ValidationException(u'Invalid Group:' + ValidationException(ObjectValidator.getFirstValidationError(group)))
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

  def __create_tzaware_datetime(self, date_time):
    utc_datetime = date_time.replace(tzinfo=dateutil.tz.tzutc())
    return utc_datetime

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
    ObjectValidator.validateDigits(self, 'tlp_level_id', minimal=0, maximal=3)
    ObjectValidator.validateDigits(self, 'status_id', minimal=0, maximal=3)
    ObjectValidator.validateDigits(self, 'published', minimal=0, maximal=1)
    ObjectValidator.validateDigits(self, 'risk_id', minimal=0, maximal=4)
    ObjectValidator.validateDigits(self, 'analysis_status_id', minimal=0, maximal=4)
    ObjectValidator.validateDigits(self, 'creator_id')
    ObjectValidator.validateDigits(self, 'modifier_id')
    ObjectValidator.validateDateTime(self, 'created')
    ObjectValidator.validateDateTime(self, 'modified')
    if self.first_seen is not None:
      ObjectValidator.validateDateTime(self, 'first_seen')
    if self.last_seen is not None:
      ObjectValidator.validateDateTime(self, 'last_seen')
    if ((self.first_seen is not None and self.last_seen is not None) and not isinstance(self.first_seen, FailedValidation) and not isinstance(self.last_seen, FailedValidation)):
      # check if date is time zone avare
      if not self.first_seen.tzinfo:
        self.first_seen = self.__create_tzaware_datetime(self.first_seen)
      if not self.last_seen.tzinfo:
        self.last_seen = self.__create_tzaware_datetime(self.last_seen)

      if self.first_seen > self.last_seen:
        setattr(self, 'first_seen',
                FailedValidation(self.first_seen,
                                 'First seen is after last seen.'))
        setattr(self, 'last_seen',
                FailedValidation(self.last_seen,
                                 'Last seen is before last seen.'))
    if self.first_seen is None and self.last_seen is not None:
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
class OldComment(BASE):
  """This is a container class for the COMMENTS table."""
  def __init__(self):
    pass

  __tablename__ = "Comments"
  identifier = Column('comment_id', Integer, primary_key=True)
  # Event witch it belongs to
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("OldEvent")
  comment = Column('comment', String)
  created = Column('created', DateTime)
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id',
                      Integer,
                      ForeignKey('Users.user_id'))

  modifier_id = Column('modifier_id',
                       Integer,
                       ForeignKey('Users.user_id'))

  def to_dict(self):
    return {'identifier': BaseClass.convert_value(self.identifier),
            'event_id': BaseClass.convert_value(self.event_id),
            'comment': BaseClass.convert_value(self.comment),
            'created': BaseClass.convert_value(self.created),
            'modified': BaseClass.convert_value(self.modified),
            'creator_id': BaseClass.convert_value(self.creator_id),
            'modifier_id': BaseClass.convert_value(self.modifier_id)
            }

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


class OldObject(BASE):
  """This is a container class for the OBJECTS table."""
  def __init__(self):
    pass

  __tablename__ = "Objects"
  identifier = Column('object_id', Integer, primary_key=True)
  attributes = relationship('OldAttribute')
  def_object_id = Column(Integer, ForeignKey('DEF_Objects.def_object_id'))
  definition = relationship(OldObjectDefinition,
                            primaryjoin='OldObjectDefinition.identifier==OldObject.def_object_id')
  created = Column('created', DateTime)
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id',
                      Integer,
                      ForeignKey('Users.user_id'))

  modifier_id = Column('modifier_id',
                       Integer,
                       ForeignKey('Users.user_id'))

  parent_object_id = Column('parentObject',
                            Integer,
                            ForeignKey('Objects.object_id'))
  parent_object = relationship('OldObject',
                               uselist=False,
                               primaryjoin='OldObject.parent_object_id==OldObject.identifier')
  children = relationship("OldObject",
                          primaryjoin='OldObject.identifier==OldObject.parent_object_id')
  event_id = Column('parentEvent', Integer, ForeignKey('Events.event_id'))

  creator_group_id = Column('creator_group_id', Integer,
                            ForeignKey('Groups.group_id'))

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

  def to_dict(self):
    attributes = list()
    for attribute in self.attributes:
      attributes.append(attribute.to_dict())

    children = list()
    for child in self.children:
      children.append(child.to_dict())
    return {'identifier': BaseClass.convert_value(self.identifier),
            'attributes': attributes,
            'def_object_id': BaseClass.convert_value(self.def_object_id),
            'definition': self.definition.to_dict(),
            'created': BaseClass.convert_value(self.created),
            'modified': BaseClass.convert_value(self.modified),
            'creator_id': BaseClass.convert_value(self.creator_id),
            'modifier_id': BaseClass.convert_value(self.modifier_id),
            'children': children,
            'event_id': BaseClass.convert_value(self.event_id),
            'creator_group_id': BaseClass.convert_value(self.creator_group_id),
            'dbcode': BaseClass.convert_value(self.dbcode),
            'uuid': BaseClass.convert_value(self.uuid),
            }

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
    if self.parent_object_id is not None:
      ObjectValidator.validateDigits(self, 'parent_object_id')
    ObjectValidator.validateDateTime(self, 'created')
    return ObjectValidator.isObjectValid(self)


class OldAttribute(BASE):
  """This is a container class for the ATTRIBUTES table."""

  __tablename__ = "Attributes"
  identifier = Column('attribute_id', Integer, primary_key=True)
  def_attribute_id = Column(Integer,
                            ForeignKey('DEF_Attributes.def_attribute_id'))
  definition = relationship(OldAttributeDefinition,
                            primaryjoin='OldAttributeDefinition.identifier==' +
                            'OldAttribute.def_attribute_id')
  object_id = Column(Integer, ForeignKey('Objects.object_id'))
  created = Column('created', DateTime)
  modified = Column('modified', DateTime)
  creator_id = Column('creator_id',
                      Integer,
                      ForeignKey('Users.user_id'))

  modifier_id = Column('modifier_id',
                       Integer,
                       ForeignKey('Users.user_id'))

  ioc = Column('ioc', Integer)
  # valuerelations
  string_value = relationship(OldStringValue,
                              primaryjoin="OldAttribute.identifier==OldStringValue.attribute_id",
                              lazy='joined', uselist=False)
  date_value = relationship(OldDateValue,
                            primaryjoin="OldAttribute.identifier==OldDateValue.attribute_id",
                            uselist=False)
  text_value = relationship(OldTextValue,
                            primaryjoin="OldAttribute.identifier==OldTextValue.attribute_id",
                            uselist=False)
  number_value = relationship(OldNumberValue,
                              primaryjoin="OldAttribute.identifier==OldNumberValue.attribute_id",
                              uselist=False)
  attr_parent_id = Column('parent_attr_id', ForeignKey('Attributes.attribute_id'))
  children = relationship('OldAttribute',
                          primaryjoin="OldAttribute.identifier==OldAttribute.attr_parent_id")
  creator_group_id = Column('creator_group_id', Integer,
                            ForeignKey('Groups.group_id'))

  __value_id = None
  internal_value = None
  __value_obj = None
  __handler_class = None
  dbcode = Column('code', Integer)
  __bit_code = None
  config = None
  uuid = Column('uuid', String)
  parent = None

  def to_dict(self):
    children = list()
    for child in self.children:
      children.append(child.to_dict())

    return {'identifier': BaseClass.convert_value(self.identifier),
            'def_attribute_id': BaseClass.convert_value(self.def_attribute_id),
            'definition': self.definition.to_dict(),
            'object_id': BaseClass.convert_value(self.object_id),
            'created': BaseClass.convert_value(self.created),
            'modified': BaseClass.convert_value(self.modified),
            'creator_id': BaseClass.convert_value(self.creator_id),
            'modifier_id': BaseClass.convert_value(self.modifier_id),
            'ioc': BaseClass.convert_value(self.ioc),
            'attr_parent_id': BaseClass.convert_value(self.attr_parent_id),
            'creator_group_id': BaseClass.convert_value(self.creator_group_id),
            'value': BaseClass.convert_value(self.plain_value),
            'children': children,
            'dbcode': BaseClass.convert_value(self.dbcode),
            'uuid': BaseClass.convert_value(self.uuid)
            }

  @property
  def shared(self):
    """
    Property shared if set it is sharable else not
    """
    if self.bit_value.is_shareable:
      return 0
    else:
      return 1

  @property
  def div_id(self):
    if self.plain_value:
      text = self.plain_value
      if hasattr(text, 'error'):
        text = text.value
      text = u'{0}'.format(text)
      return re.sub(r'[^\w]', '', text)
    else:
      return 'NotDefined'

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
    if self.string_value is not None:
      value = self.string_value
    elif self.date_value is not None:
      value = self.date_value
    elif self.text_value is not None:
      value = self.text_value
    elif self.number_value is not None:
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
    # Take into account the failed validation objects
    if isinstance(self.__value_obj, FailedValidation):
      self.internal_value = self.__value_obj
    else:
      try:
        self.internal_value = self.__value_obj.value
      except AttributeError:
        pass
    return self.internal_value

  def __set_value(self, value):
    if self.__value_obj is None:
      self.__value_obj = self.__get_value_obj()
    # Take into account the failed validation objects
    if isinstance(self.__value_obj, FailedValidation):
      self.internal_value = self.__value_obj
    else:
      try:
        self.__value_obj.value = value
        self.internal_value = self.__value_obj.value
      except AttributeError:
        pass

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
      raise Exception(u'Empty value')
    else:
      return value

  @property
  def value(self):
    """
    Alias for plain_value
    """
    return self.plain_value

  @value.setter
  def value(self, new_value):
    """
    Plain value setter, somehow :)
    """
    # check first if not already set
    try:
      value = self.plain_value
    except Exception:
      value = None
    if value:
      self.__set_value(new_value)
    else:
      if self.definition:
        classname = getattr(self.definition, 'classname')
        value_instance = get_class('ce1sus.brokers.valuebroker', classname)()
        value_instance.attribute_id = self.identifier
        value_instance.attribute = self
        value_instance.value = new_value
        if self.object:
          value_instance.event = getattr(self.object, 'event')
        else:
          raise Exception(u'No object was specified')
        # set the value
        attr_name = classname.replace('V', '_v').lower()
        setattr(self, attr_name, value_instance)
      else:
        raise Exception(u'No definition was specified')

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
    # TODO: encoding error
    ObjectValidator.validateRegex(value_obj,
                                  'value',
                                  getattr(self.definition, 'regex'),
                                  u'The value "{0}" does not match {1} for definition {2}'.format(value_obj.value,
                                                                                                  getattr(self.definition, 'regex'),
                                                                                                  getattr(self.definition, 'name')).encode('utf-8'),
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
