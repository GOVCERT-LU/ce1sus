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
from sqlalchemy.types import DateTime
from ce1sus.brokers.permission.permissionclasses import User, Group
from dagr.helpers.validator.objectvalidator import ObjectValidator, \
                                                   FailedValidation
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition
from ce1sus.brokers.staticbroker import Status, Risk, Analysis, TLPLevel

_REL_GROUPS_EVENTS = Table('Groups_has_Events', BASE.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)
_OBJECT_CROSSREFERENCE = Table('Obj_links_Obj', BASE.metadata,
    Column('object_id_to', Integer, ForeignKey('Objects.object_id')),
    Column('object_id_from', Integer, ForeignKey('Objects.object_id'))
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
    if not self.first_seen is None and not self.last_seen is None:
      if self.first_seen < self.last_seen:
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

  def toDict(self, full=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['identifier'] = self.identifier
    result[self.__class__.__name__]['title'] = self.title
    result[self.__class__.__name__]['description'] = '{0}'.format(
                                                              self.description)
    result[self.__class__.__name__]['first_seen'] = '{0}'.format(
                                                              self.first_seen)
    result[self.__class__.__name__]['last_seen'] = '{0}'.format(self.last_seen)
    result[self.__class__.__name__]['modified'] = '{0}'.format(self.modified)
    result[self.__class__.__name__]['tlp'] = self.tlp.text
    result[self.__class__.__name__]['published'] = self.published
    result[self.__class__.__name__]['status'] = self.stauts
    result[self.__class__.__name__]['risk'] = self.risk
    result[self.__class__.__name__]['analysis'] = self.analysis
    result[self.__class__.__name__]['groups'] = list()
    if full:
      for group in self.groups:
        result[self.__class__.__name__]['groups'].append(group.toDict())
    result[self.__class__.__name__]['creator'] = self.creator.toDict()
    result[self.__class__.__name__]['modifier'] = self.modifier.toDict()
    result[self.__class__.__name__]['objects'] = list()
    if full:
      for obj in self.objects:
        result[self.__class__.__name__]['objects'].append(obj.toDict(True))
      result[self.__class__.__name__]['comments'] = list()
    if full:
      for comment in self.comments:
        result[self.__class__.__name__]['comments'].append(comment.toDict())

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

  def toDict(self, full=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['identifier'] = self.identifier
    result[self.__class__.__name__]['event_id'] = self.event_id
    result[self.__class__.__name__]['comment'] = self.comment
    result[self.__class__.__name__]['created'] = '{0}'.format(self.created)
    result[self.__class__.__name__]['modified'] = '{0}'.format(self.modified)
    result[self.__class__.__name__]['creator'] = self.creator.toDict()
    result[self.__class__.__name__]['modifier'] = self.modifier.toDict()

    return result


class Object(BASE):
  """This is a container class for the OBJECTS table."""
  def __init__(self):
    pass

  __tablename__ = "Objects"
  identifier = Column('object_id', Integer, primary_key=True)
  attributes = relationship('Attribute', backref="objects")
  def_object_id = Column(Integer, ForeignKey('DEF_Objects.def_object_id'))
  definition = relationship(ObjectDefinition,
                            primaryjoin='ObjectDefinition.identifier' +
                            '==Object.def_object_id', innerjoin=True)

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
  # TODO: Fix Me! - FK removed due to errors
  parentEvent_id = Column('parentEvent', Integer)

  children = relationship("Object", primaryjoin='Object.identifier' +
                         '==Object.parentObject_id')

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

  def toDict(self, full=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['identifier'] = self.identifier
    result[self.__class__.__name__]['event_id'] = self.event_id
    result[self.__class__.__name__]['parentObject_id'] = self.parentObject_id
    result[self.__class__.__name__]['parentEvent_id'] = self.parentEvent_id
    result[self.__class__.__name__]['definition'] = self.definition.toDict(
                                                                        True
                                                                        )
    result[self.__class__.__name__]['attributes'] = list()
    if full:
      for attribute in self.attributes:
        result[self.__class__.__name__]['attributes'].append(
                                                        attribute.toDict(True))
    return result


# pylint: disable=R0903
class ObjectAttributeRelation(BASE):
  """This is a container class for the ATTRIBUTES table."""

  def __init__(self):
    pass

  __tablename__ = "Attribute_Object_Relations"
  identifier = Column('AOR_id', Integer, primary_key=True)
  object_id = Column(Integer, ForeignKey('Objects.object_id'))
  object = relationship(Object,
          primaryjoin="ObjectAttributeRelation.object_id==Object.identifier")
  attribute_id = Column('attribute_id',
                        Integer,
                        ForeignKey('Attributes.attribute_id'))
  attribute = relationship('Attribute',
    primaryjoin="ObjectAttributeRelation.attribute_id==Attribute.identifier")
  sameAttribute_id = Column('ref_attribute_id',
                            Integer,
                            ForeignKey('Attributes.attribute_id'))
  sameAttribute = relationship('Attribute',
  primaryjoin="ObjectAttributeRelation.sameAttribute_id==Attribute.identifier")

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateDigits(self, 'attribute_id')
    ObjectValidator.validateDigits(self, 'object_id')
    ObjectValidator.validateDigits(self, 'sameAttribute_id')
    return ObjectValidator.isObjectValid(self)

  def toDict(self, full=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['identifier'] = self.identifier
    result[self.__class__.__name__]['object_id'] = self.name
    result[self.__class__.__name__]['attribute_id'] = self.description
    result[self.__class__.__name__]['sameattribute_id'] = list()

    return result
