from ce1sus.brokers.classes.static import Status, TLP_Level

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 5, 2013

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ce1sus.db.session import Base
from sqlalchemy.types import DateTime
from ce1sus.brokers.classes.permissions import User
from ce1sus.brokers.classes.definitions import DEF_Attribute, DEF_Object
import ce1sus.helpers.validator as validator

class Ticket(Base):
  __tablename__ = "Tickets"

  identifier = Column('ticked_id', Integer, primary_key=True)
  created = Column('created', DateTime)
  ticket = Column('ticket', String)
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship(User, uselist=False, primaryjoin='User.identifier==Ticket.user_id', innerjoin=True)


class Attribute(Base):
  __tablename__ = "Attributes"

  identifier = Column('attribute_id', Integer, primary_key=True)

  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship(User, uselist=False, primaryjoin='User.identifier==Attribute.user_id', innerjoin=True)

  def_attribute_id = Column(Integer, ForeignKey('DEF_Attributes.def_attribute_id'))
  definition = relationship(DEF_Attribute, primaryjoin='DEF_Attribute.identifier==Attribute.def_attribute_id', innerjoin=True)

  object_id = Column(Integer, ForeignKey('Objects.object_id'))
  object = relationship("Object", primaryjoin='Object.identifier==Attribute.object_id')

  __value = None

  @property
  def key(self):
    return self.definition.name

  @property
  def value(self):
    return self.__value

  @value.setter
  def value(self, value):
    self.__value = value

  def validate(self):
    validator.validateAlNum(self, 'value', True)
    validator.validateDigits(self, 'def_attribute_id')
    return validator.isObjectValid(self)


relationTicketsEvents = Table('Events_has_Tickets', Base.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('ticked_id', Integer, ForeignKey('Tickets.ticked_id'))
)

relationGroupsEvents = Table('Groups_has_Events', Base.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)

eventsCrossReference = Table('Event_links_Event', Base.metadata,
    Column('event_id_from', Integer, ForeignKey('Events.event_id')),
    Column('event_id_to', Integer, ForeignKey('Events.event_id'))
)


class Event(Base):
  __tablename__ = "Events"

  identifier = Column('event_id', Integer, primary_key=True)

  label = Column('short_description', String)
  description = Column('description', String)

  created = Column('created', DateTime)
  first_seen = Column('first_seen', DateTime)
  last_seen = Column('last_seen', DateTime)
  modified = Column('modified', DateTime)

  tlp_level_id = Column('tlp_level', Integer)
  published = Column('published', Integer)
  status_id = Column('status', Integer)

  comments = relationship("Comment", backref="Events")


  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship('User', innerjoin=True)

  tickets = relationship("Ticket", secondary=relationTicketsEvents, backref="Tickets")

  # groups = relationship("Group")


  objects = relationship('Object', backref="Events")
  __tlpObj = None
  def addObject(self, obj):
    self.objects.append(obj)

  @property
  def stauts(self):
    return Status.getByID(self.status_id)

  @property
  def tlp(self):
    if self.__tlpObj is None:
      self.__tlpObj = TLP_Level(self.tlp_level_id)
    return self.__tlpObj


  def validate(self):
    validator.validateAlNum(self, 'label')
    validator.validateAlNum(self, 'description', True)
    validator.validateDigits(self, 'tlp_level_id')
    validator.validateDigits(self, 'status_id')
    validator.validateDigits(self, 'published')
    return validator.isObjectValid(self)

class Comment(Base):
  __tablename__ = "Comments"

  identifier = Column('comment_id', Integer, primary_key=True)
  # Creator
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship('User', innerjoin=True)
  # Event witch it belongs to
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event")



objectsCrossReference = Table('Obj_links_Obj', Base.metadata,
    Column('object_id_to', Integer, ForeignKey('Objects.object_id')),
    Column('object_id_from', Integer, ForeignKey('Objects.object_id'))
)

class Object(Base):
  __tablename__ = "Objects"

  identifier = Column('object_id', Integer, primary_key=True)

  attributes = relationship(Attribute, backref="objects")

  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship("User", uselist=False, primaryjoin='User.identifier==Object.user_id', innerjoin=True)


  def_object_id = Column(Integer, ForeignKey('DEF_Objects.def_object_id'))
  definition = relationship(DEF_Object, primaryjoin='DEF_Object.identifier==Object.def_object_id', innerjoin=True)

  objects = relationship("Object", secondary=objectsCrossReference,
                         primaryjoin='Obj_links_Obj.c.object_id_to==Object.identifier',
                         secondaryjoin='Obj_links_Obj.c.object_id_from==Object.identifier',
                         backref="children")

  created = Column('created', DateTime, primary_key=True)

  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False, primaryjoin='Event.identifier==Object.event_id', innerjoin=True)

  def addAttribute(self, attribute):
    self.attributes.append(attribute)

  def validate(self):
    validator.validateDigits(self, 'user_id')
    validator.validateDigits(self, 'def_object_id')
    validator.validateDigits(self, 'event_id')
    return validator.isObjectValid(self)

class StringValue(Base):
  __tablename__ = "StringValues"

  identifier = Column('StringValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)


class DateValue(Base):
  __tablename__ = "DateValues"

  identifier = Column('DateValue_id', Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)


class TextValue(Base):
  __tablename__ = "TextValues"

  identifier = Column('TextValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)
class NumberValue(Base):
  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)
