"""This module provides container classes and interfaces
for inserting data into the database.
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 9, 2013


from ce1sus.db.broker import BrokerBase, ValidationException, \
NothingFoundException, TooManyResultsFoundException, OperationException
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, String, ForeignKey, Table, not_
from sqlalchemy.orm import relationship
from ce1sus.db.session import BASE
from sqlalchemy.types import DateTime
from ce1sus.brokers.permissionbroker import User, Group
import ce1sus.helpers.validator as validator
from ce1sus.brokers.definitionbroker import AttributeDefinition, \
    ObjectDefinition, AttributeDefinitionBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel
from sqlalchemy.sql.expression import or_, and_





class Attribute(BASE):
  """This is a container class for the ATTRIBUTES table."""
  __tablename__ = "Attributes"

  identifier = Column('attribute_id', Integer, primary_key=True)

  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship(User, uselist=False,
              primaryjoin='User.identifier==Attribute.user_id', innerjoin=True)

  def_attribute_id = Column(Integer,
                            ForeignKey('DEF_Attributes.def_attribute_id'))
  definition = relationship(AttributeDefinition,
              primaryjoin='AttributeDefinition.identifier==' +
              'Attribute.def_attribute_id', innerjoin=True)

  object_id = Column(Integer, ForeignKey('Objects.object_id'))
  object = relationship("Object",
                        primaryjoin='Object.identifier==Attribute.object_id')
  value_id = 0

  __value = None

  @property
  def key(self):
    """
    returns the name of the definition

    :returns: String
    """
    return self.definition.name

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

    validator.validateDigits(self, 'def_attribute_id')
    return validator.isObjectValid(self)



_REL_GROUPS_EVENTS = Table('Groups_has_Events', BASE.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
)

_EVENTS_CROSSREFENRECE = Table('Event_links_Event', BASE.metadata,
    Column('event_id_from', Integer, ForeignKey('Events.event_id')),
    Column('event_id_to', Integer, ForeignKey('Events.event_id'))
)

_REL_TICKET_EVENTS = Table('Events_has_Tickets', BASE.metadata,
    Column('event_id', Integer, ForeignKey('Events.event_id')),
    Column('ticked_id', Integer, ForeignKey('Tickets.ticked_id'))
)



class Event(BASE):
  """This is a container class for the EVENTS table."""
  __tablename__ = "Events"

  identifier = Column('event_id', Integer, primary_key=True)

  title = Column('title', String)
  description = Column('description', String)

  created = Column('created', DateTime)
  first_seen = Column('first_seen', DateTime)
  last_seen = Column('last_seen', DateTime)
  modified = Column('modified', DateTime)

  tlp_level_id = Column('tlp_level_id', Integer)
  published = Column('published', Integer)
  status_id = Column('status_id', Integer)

  comments = relationship("Comment", backref="Events")

  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship('User', innerjoin=True)

  tickets = relationship("Ticket", secondary=_REL_TICKET_EVENTS,
                              backref="events")



  groups = relationship(Group, secondary='Groups_has_Events', backref="events")


  objects = relationship('Object', backref="Events")
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
    self.objects.append(obj)

  @property
  def stauts(self):
    """
    returns the status

    :returns: String
    """
    return Status.getByID(self.status_id)

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
    self.groups.append(group)

  def removeGroup(self, group):
    """
    Remove a group to this event

    :param group: Group to be removes
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be removed is invalid')
    self.groups.remove(group)

  def addTicket(self, ticket):
    """
    Add a Ticket to this event

    :param ticket: Ticket to be added
    :type ticket: Ticket
    """
    errors = not ticket.validate()
    if errors:
      raise ValidationException('Ticket to be added is invalid')
    self.tickets.append(ticket)

  def removeTicket(self, ticket):
    """
    Remove a Ticket to this event

    :param ticket: Ticket to be removes
    :type ticket: Ticket
    """
    errors = not ticket.validate()
    if errors:
      raise ValidationException('Ticket to be removed is invalid')
    self.tickets.remove(ticket)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    validator.validateAlNum(self, 'title')
    validator.validateAlNum(self, 'description', True)
    validator.validateDigits(self, 'tlp_level_id')
    validator.validateDigits(self, 'status_id')
    validator.validateDigits(self, 'published')
    return validator.isObjectValid(self)

class Ticket(BASE):
  """This is a container class for the TICKETS table."""
  # TODO: Finalize Ticket
  __tablename__ = "Tickets"

  identifier = Column('ticked_id', Integer, primary_key=True)
  created = Column('created', DateTime)
  ticket = Column('ticket', String)
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship(User, uselist=False,
              primaryjoin='User.identifier==Ticket.user_id', innerjoin=True)


  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO validation of tickets
    return validator.isObjectValid(self)


class Comment(BASE):
  """This is a container class for the COMMENTS table."""

  # TODO: Finalize comments
  __tablename__ = "Comments"

  identifier = Column('comment_id', Integer, primary_key=True)
  # Creator
  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship('User', innerjoin=True)
  # Event witch it belongs to
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event")

  comment = Column('comment', String)
  created = Column('created', DateTime)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    validator.validateDigits(self, 'user_id')
    validator.validateDigits(self, 'event_id')
    # TODO find way to validate this!
    # validator.validateAlNum(self, 'comment', True, True)
    return validator.isObjectValid(self)

_OBJECT_CROSSREFERENCE = Table('Obj_links_Obj', BASE.metadata,
    Column('object_id_to', Integer, ForeignKey('Objects.object_id')),
    Column('object_id_from', Integer, ForeignKey('Objects.object_id'))
)

class Object(BASE):
  """This is a container class for the OBJECTS table."""
  __tablename__ = "Objects"

  identifier = Column('object_id', Integer, primary_key=True)

  attributes = relationship(Attribute, backref="objects")

  user_id = Column(Integer, ForeignKey('Users.user_id'))
  creator = relationship("User", uselist=False,
                         primaryjoin='User.identifier==Object.user_id',
                         innerjoin=True)


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

  created = Column('created', DateTime, primary_key=True)

  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False, primaryjoin='Event.identifier' +
                       '==Object.event_id', innerjoin=True)

  def addAttribute(self, attribute):
    """
    Add an attribute to this event

    :param attribute: Attribute to be added
    :type attribute: Attribute
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be added is invalid')
    self.attributes.append(attribute)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    validator.validateDigits(self, 'user_id')
    validator.validateDigits(self, 'def_object_id')
    validator.validateDigits(self, 'event_id')
    return validator.isObjectValid(self)

class StringValue(BASE):
  """This is a container class for the STRINGVALUES table."""
  __tablename__ = "StringValues"

  identifier = Column('StringValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # validator.validateAlNum(self, 'value', True)
    return validator.isObjectValid(self)


class DateValue(BASE):
  """This is a container class for the DATEVALES table."""
  __tablename__ = "DateValues"

  identifier = Column('DateValue_id', Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Validator for dates
    return True


class TextValue(BASE):
  """This is a container class for the TEXTVALUES table."""
  __tablename__ = "TextValues"

  identifier = Column('TextValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # validator.validateAlNum(self, 'value', True)
    return validator.isObjectValid(self)


class NumberValue(BASE):
  """This is a container class for the NUMBERVALUES table."""
  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False, innerjoin=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # validator.validateDigits(self, 'value')
    return validator.isObjectValid(self)


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
    obj = self.getByID(identifier)
    # remove attributes
    try:
      self.attributeBroker.removeAttributeList(obj.attributes, False)
      self.session.flush()
      BrokerBase.removeByID(self, obj.identifier, False)
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except Exception as e:
      self.getLogger().info(e)
      self.session.rollback()

class ValueBroker(BrokerBase):
  """
  This broker is used internally to serparate the values to their corresponding tables

  Note: Only used by the AttributeBroker
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.__clazz = StringValue

  @property
  def clazz(self):
    """
    returns the class used for this value broker

    Note: May vary during its lifetime

    """
    return self.__clazz

  @clazz.setter
  def clazz(self, clazz):
    """
    setter for the class
    """
    self.__clazz = clazz

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return self.__clazz

  def __setClassByAttribute(self, attribute):
    """
    sets class for the attribute

    :param attribute: the attribute in context
    :type attribute: Attribute
    """
    className = attribute.definition.className
    self.__clazz = globals()[className]

  def __convertAttriuteValueToValue(self, attribute):
    """
    converts an Attribute to a XXXXXValue object

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns: XXXXXValue
    """
    valueInstance = self.__clazz()
    valueInstance.value = attribute.value
    valueInstance.identifier = attribute.value_id
    valueInstance.attribute_id = attribute.identifier

    return valueInstance

  def getByAttribute(self, attribute):
    """
    fetches one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """

    self.__setClassByAttribute(attribute)

    try:
      result = self.session.query(self.getBrokerClass()).filter(
              self.getBrokerClass().attribute_id == attribute.identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found with ID :{0} in {1}'.format(
                                  attribute.identifier, self.getBrokerClass()))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
          'Too many value found for ID :{0} in {1}'.format(attribute.identifier,
           self.getBrokerClass()))

    return result

  def inserByAttribute(self, attribute, commit=True):
    """
    Inserts one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be inserted is invalid')

    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)



    BrokerBase.insert(self, value, commit)

  def updateByAttribute(self, attribute, commit=True):
    """
    updates one XXXXXValue instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : XXXXXValue
    """

    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be updated is invalid')

    self.__setClassByAttribute(attribute)
    value = self.__convertAttriuteValueToValue(attribute)
    BrokerBase.update(self, value, commit)

  def removeByAttribute(self, attribute, commit):
    """
    Removes one XXXXXValue with the information given by the attribtue

    :param attribute: the attribute in context
    :type attribute: Attribute
    :param commit: do a commit after
    :type commit: Boolean
    """
    self.__setClassByAttribute(attribute)

    try:
      self.session.query(self.getBrokerClass()).filter(
                      self.getBrokerClass().attribute_id == attribute.identifier
                      ).delete(synchronize_session='fetch')
    except sqlalchemy.exc.OperationalError as e:
      raise OperationException(e)
    if commit:
      self.session.commit()
    else:
      self.session.flush()


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
      attribute.value = value.value
      attribute.value_id = value.identifier
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No value found for attribute :{0}'.format(
                                                  attribute.definition.name))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
            'Too many results found for attribute :{0}'.format(
                                    attribute.definition.name))

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

    # getdefinition
    definition = self.attributeDefinitionBroker.getByID(instance.def_attribute_id)


    validator.validateRegex(instance, 'value', definition.regex, 'The value does not match {0}'.format(definition.regex) , False)

    errors = not instance.validate()
    if errors:
      raise ValidationException('Attribute to be inserted is invalid')
    try:
      BrokerBase.insert(self, instance, False)
      self.session.flush()
      # insert value for value table
      self.valueBroker.inserByAttribute(instance, False)
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except Exception as e:
      self.getLogger().info(e)
      self.session.rollback()

  def update(self, instance, commit=True):
    """
    overrides BrokerBase.update
    """
    # validation of the value of the attribute first

    # getdefinition
    definition = self.attributeDefinitionBroker.getByID(instance.def_attribute_id)


    validator.validateRegex(instance, 'value', definition.regex, 'The value does not match {0}'.format(definition.regex) , False)

    errors = not instance.validate()
    if errors:
      raise ValidationException('Attribute to be updated is invalid')

    try:
      BrokerBase.update(self, instance, False)
      # updates the value of the value table
      self.session.flush()
      self.valueBroker.updateByAttribute(instance, False)
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except Exception as e:
      self.getLogger().info(e)
      self.session.rollback()

  def removeByID(self, identifier, commit=True):
    attribute = self.getByID(identifier)
    try:
      self.valueBroker.removeByAttribute(attribute, False)
      # first remove values
      self.session.flush()
      # remove attribute
      BrokerBase.removeByID(self, identifier=attribute.identifier, commit=False)
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except Exception as e:
      self.getLogger().info(e)
      self.session.rollback()



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
        self.session.flush()
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except Exception as e:
      self.getLogger().info(e)
      self.session.rollback()


class TicketBroker(BrokerBase):
  """
  This broker handles all operations on ticket objects
  """
  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Ticket

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
    for obj in event.objects:
      for attribute in obj.attributes:
        self.attributeBroker.getSetValues(attribute)
    return event

  def insert(self, instance):
    """
    overrides BrokerBase.insert
    """

    errors = not instance.validate()
    if errors:
      raise ValidationException('Event to be inserted is invalid')

    BrokerBase.insert(self, instance)
    # insert value for value table
    for obj in instance.objects:
      for attribute in obj.attributes:
        self.attributeBroker.insert(attribute)

  def update(self, instance):
    """
    overrides BrokerBase.update
    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Event to be inserted is invalid')

    BrokerBase.update(self, instance)
    # insert value for value table
    # TODO: check this ..... and also validation


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
      groups = list()
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
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or event not found')
    event.addGroup(group)
    if commit:
      self.session.commit()
    else:
      self.session.flush()

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
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    event.removeGroup(group)
    if commit:
      self.session.commit()
    else:
      self.session.flush()



