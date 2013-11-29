# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import  ValidationException
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from dagr.db.session import BASE
from dagr.helpers.validator.objectvalidator import ObjectValidator
from dagr.helpers.hash import hashSHA1
from sqlalchemy.ext.hybrid import hybrid_property
from ce1sus.api.restclasses import RestObjectDefinition, \
                                   RestAttributeDefinition


_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'DObj_has_DAttr', BASE.metadata,
    Column('def_attribute_id', Integer, ForeignKey(
                                          'DEF_Attributes.def_attribute_id')),
    Column('def_object_id', Integer, ForeignKey('DEF_Objects.def_object_id'))
    )


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
  dbchksum = Column('chksum', String)
  share = Column('sharable', Integer)

  @hybrid_property
  def chksum(self):
    if self.dbchksum:
      return self.dbchksum
    else:
      if self.name:
        self.dbchksum = hashSHA1(self.name)
      else:
        raise UnboundLocalError

  @chksum.setter
  def chksum(self, chksum):
    self.dbchksum = chksum

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
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=5,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)

  def toRestObject(self):
    result = RestObjectDefinition()
    result.name = self.name
    result.description = self.description

    return result


class AttributeDefinition(BASE):
  """This is a container class for the DEF_ATTRIBUTES table."""
  def __init__(self):
    pass

  __tableDefinitions = {0: 'TextValue',
                 1: 'StringValue',
                 2: 'DateValue',
                 3: 'NumberValue'}

  __handlerDefinitions = {0: 'generichandler.GenericHandler',
                          1: 'filehandler.FileWithHashesHandler',
                          2: 'tickethandler.TicketHandler',
                          3: 'tickethandler.CVEHandler',
                          4: 'locationhandler.LocationHandler',
                          5: 'multiplegenerichandler.MultipleGenericHandler',
                          6: 'filehandler.FileHandler',
                          7: 'datehandler.DateHandler',
                          8: 'cbvaluehandler.CBValueHandler'}

  __tablename__ = "DEF_Attributes"
  # table class mapping
  identifier = Column('def_attribute_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  regex = Column('regex', String)
  classIndex = Column(Integer)
  handlerIndex = Column(Integer)
  deletable = Column('deletable', Integer)
  # note class relationTable attribute
  objects = relationship('ObjectDefinition', secondary='DObj_has_DAttr',
                         back_populates='attributes', cascade='all')
  share = Column('sharable', Integer)
  relation = Column('relationable', Integer)
  dbchksum = Column('chksum', String)

  @hybrid_property
  def chksum(self):
    if self.dbchksum:
      return self.dbchksum
    else:
      if self.name:
        key = '{0}{1}{2}'.format(self.name, self.regex, self.classIndex, self.handlerIndex)
        self.dbchksum = hashSHA1(key)
        return self.dbchksum
      else:
        raise UnboundLocalError

  @chksum.setter
  def chksum(self, chksum):
    self.dbchksum = chksum

  @property
  def className(self):
    """The name for the class used for storing the attribute value"""
    if not self.classIndex is None:
      return self.findClassName(self.classIndex)
    else:
      return ''

  @property
  def handlerName(self):
    """The name of the handler used"""
    if not self.handlerIndex is None:
      return self.findHandlerName(self.handlerIndex)
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
    if index < 0 and index >= len(self.__tableDefinitions):
      raise Exception('Invalid input "{0}"'.format(index))
    return self.__tableDefinitions[index]

  def findHandlerName(self, index):
    """
    returns the handler name

    :param index: index of the class name
    :type index: Integer

    :returns: String
    """
    # Test if the index is
    if index < 0 and index >= len(self.__handlerDefinitions):
      raise Exception('Invalid input "{0}"'.format(index))
    return self.__handlerDefinitions[index]

  def findTableIndex(self, name):
    """
    searches for the index for the given table name

    :param index: class name
    :type index: String

    :returns: Integer
    """
    result = None
    for index, tableName in self.__tableDefinitions.iteritems():
      if tableName == name:
        result = index
        break
    return result

  @staticmethod
  def getTableDefinitions(simple=True):
    """ returns the table definitions where the key is the value and value the
    index of the tables.

    Note: Used for displaying the definitions of the tables in combo boxes

    :returns: Dictionary
    """
    result = dict()
    for index, tableName in AttributeDefinition.__tableDefinitions.iteritems():
      if simple:
        key = tableName.replace('Value', '')
      else:
        key = tableName
      value = index
      result[key] = value
    return result

  @staticmethod
  def getHandlerDefinitions():
    """ returns the table definitions where the key is the value and value the
    index of the tables.

    Note: Used for displaying the definitions of the tables in combo boxes

    :returns: Dictionary
    """
    result = dict()
    for index, handlerName in (AttributeDefinition.
                                        __handlerDefinitions.iteritems()):
      key = handlerName.split('.')[1]
      value = index
      result[key] = value
    return result

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'name', withSpaces=True,
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateRegularExpression(self, 'regex')
    ObjectValidator.validateDigits(self, 'classIndex')
    ObjectValidator.validateDigits(self, 'handlerIndex')
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

  def toRestObject(self):
    result = RestAttributeDefinition()
    result.description = self.description
    result.name = self.name
    result.regex = self.regex
    result.classIndex = self.classIndex
    result.relation = self.relation

    return result
