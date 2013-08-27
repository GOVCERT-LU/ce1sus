"""This module provides container classes and interfaces
for inserting data into the database.
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# Created on Jul 5, 2013

import re
from framework.db.broker import BrokerBase, ValidationException, \
 NothingFoundException, BrokerException
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from framework.db.session import BASE
from framework.helpers.validator import ObjectValidator



_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'DObj_has_DAttr', BASE.metadata,
    Column('def_attribute_id', Integer, ForeignKey(
                                          'DEF_Attributes.def_attribute_id')),
    Column('def_object_id', Integer, ForeignKey('DEF_Objects.def_object_id'))
    )


class AttributeDefinition(BASE):
  """This is a container class for the DEF_ATTRIBUTES table."""
  def __init__(self):
    pass

  __definitions = {0 : 'TextValue',
                 1 : 'StringValue',
                 2 : 'DateValue',
                 3 : 'NumberValue',
                 4 : 'FileValue'}

  __tablename__ = "DEF_Attributes"
  # table class mapping
  identifier = Column('def_attribute_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  regex = Column('regex', String)
  classIndex = Column(Integer)

  # note class relationTable attribute

  objects = relationship('ObjectDefinition', secondary='DObj_has_DAttr',
                         back_populates='attributes', cascade='all')


  @property
  def className(self):
    """The name for the class used for storing the attribute value"""
    if not self.classIndex is None:
      return self.findClassName(self.classIndex)
    else:
      return ''

  def findClassName(self, index):
    """
    returns the table name

    :param index: index of the class name
    :type index: Integer

    :returns: String
    """
    # Test if the index is
    if index < 0 and index >= len(self.__definitions):
      raise Exception('Invalid input "{0}"'.format(index))
    return self.__definitions[index]

  def findTableIndex(self, name):
    """
    searches for the index for the given table name

    :param index: class name
    :type index: String

    :returns: Integer
    """
    result = None
    for index, tableName in self.__definitions.iteritems():
      if tableName == name:
        result = index
        break
    return result


  @staticmethod
  def getTableDefinitions():
    """ returns the table definitions where the key is the value and value the
    index of the tables.

    Note: Used for displaying the definitions of the tables in combo boxes

    :returns: Dictionary
    """
    result = dict()
    for index, tableName in AttributeDefinition.__definitions.iteritems():
      key = tableName.replace('Value', '')
      value = index
      result[key] = value
    return result

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'name', withSpaces=True,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    # TODO: Find a way to validate regexes
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!
    -> compile to validate to test regex!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!
    """
    ObjectValidator.validateDigits(self, 'classIndex')
    return ObjectValidator.isObjectValid(self)

  def addObject(self, obj):
    """
    Add an object to this attribute$

    :param obj: Object to be added
    :type obj: Object
    """
    function = getattr(self.objects, 'append')
    function(obj)

  def removeObject(self, obj):
    """
    Removes an object from this attribute$

    :param obj: Object to be removed
    :type obj: Object
    """
    function = getattr(self.objects, 'remove')
    function(obj)



class ObjectDefinition(BASE):
  """This is a container class for the DEF_Objects table."""
  def __init__(self):
    pass

  __tablename__ = "DEF_Objects"
  # table class mapping
  identifier = Column('def_object_id', Integer, primary_key=True)
  name = Column('name', String, nullable=False)
  description = Column('description', String)

  attributes = relationship('AttributeDefinition', secondary='DObj_has_DAttr',
                            back_populates='objects', cascade='all')

  def addAttribute(self, attribute):
    """
    Add an attribute to this object

    :param attribute: Attribute to be added
    :type attribute: AttributeDefinition
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be added is invalid')
    function = getattr(self.attributes, 'append')
    function(attribute)


  def removeAttribute(self, attribute):
    """
    Removes an attribute from this object

    :param obj: Object to be removed
    :type obj: Object
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException('Attribute to be removed is invalid')
    function = getattr(self.attributes, 'remove')
    function(attribute)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self,
                                  'name',
                                  withSpaces=True,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)



class AttributeDefinitionBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return AttributeDefinition

  def getObjectsByAttribute(self, identifier, belongIn=True):
    """
    returns all objects belonging to an attribute with the given identifier

    Note: If nothing is found an empty list is returned

    :param identifier: identifier of the object
    :type identifier: Integer
    :param belongIn: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belongIn: Boolean

    :returns: list of ObjectDefinitons
    """
    try:

      objects = self.session.query(ObjectDefinition).join(
                                              AttributeDefinition.objects
                                              ).filter(
                                        AttributeDefinition.identifier ==
                                        identifier).all()
      if not belongIn:
        objIDs = list()
        for obj in objects:
          objIDs.append(obj.identifier)
        objects = self.session.query(ObjectDefinition).filter(
 ~ObjectDefinition.identifier.in_(objIDs))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return objects

  def getCBValues(self, objIdentifier):
    """
    returns the values for a combo box where the key is the name of the
    attribute and the value is the identifier.

    :returns: Dictionary
    """


    definitions = list()
    try:
      definitions = self.session.query(AttributeDefinition).join(
                                              AttributeDefinition.objects
                                              ).filter(
                                        ObjectDefinition.identifier ==
                                        objIdentifier).order_by(
                                        AttributeDefinition.name).all()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().debug(e)

    result = dict()
    for definition in definitions:
      result[definition.name] = (definition.identifier, definition.description)
    return result

  def addObjectToAttribute(self, objID, attrID, commit=True):
    """
    Add an attribute to an object

    :param objID: Identifier of the object
    :type objID: Integer
    :param attrID: Identifier of the attribute
    :type attrID: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == objID).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
      self.getLogger().error(e)
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)
    attribute.addObject(obj)

    self.doCommit(commit)


  def removeObjectFromAttribute(self, objID, attrID, commit=True):
    """
    Removes an attribute from an object

    :param objID: Identifier of the object
    :type objID: Integer
    :param attrID: Identifier of the attribute
    :type attrID: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == objID).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)
    attribute.removeObject(obj)

    self.doCommit(commit)


class ObjectDefinitionBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return ObjectDefinition

  def getAttributesByObject(self, identifier, belongIn=True):
    """
    returns all attributes belonging to an object with the given identifier

    Note: If nothing is found an empty list is returned

    :param identifier: identifier of the attribute
    :type identifier: Integer
    :param belongIn: If set returns all the objects of the attribute else
                     all the objects not belonging to the attribute
    :type belongIn: Boolean

    :returns: list of AttributeDefinitions
    """
    try:

      attributes = self.session.query(AttributeDefinition).join(
                                          ObjectDefinition.attributes).filter(
                                          ObjectDefinition.identifier ==
                                          identifier).all()
      if not belongIn:
        attributeIDs = list()
        for attribute in attributes:
          attributeIDs.append(attribute.identifier)
        attributes = self.session.query(AttributeDefinition).filter(
 ~AttributeDefinition.identifier.in_(attributeIDs))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)
    return attributes


  def getCBValues(self):
    """
    returns the values for a combo box where the key is the name of the
    attribute and the value is the identifier.

    :returns: Dictionary
    """
    definitions = self.getAll()
    result = dict()
    for definition in definitions:
      result[definition.name] = (definition.identifier, definition.description)
    return result


  def addAttributeToObject(self, attrID, objID, commit=True):
    """
    Add an object to an attribute

    :param objID: Identifier of the object
    :type objID: Integer
    :param attrID: Identifier of the attribute
    :type attrID: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == objID).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    # except sqlalchemy.exc.SQLAlchemyError as e:
    #  self.getLogger().fatal(e)

    obj.addAttribute(attribute)

    self.doCommit(commit)

  def removeAttributeFromObject(self, attrID, objID, commit=True):
    """
    Removes an object from an attribute

    :param objID: Identifier of the object
    :type objID: Integer
    :param attrID: Identifier of the attribute
    :type attrID: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == objID).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attrID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    obj.removeAttribute(attribute)

    self.doCommit(commit)


