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
from ce1sus.common.handlers.base import HandlerBase, HandlerException
import json
from ce1sus.common.ce1susutils import get_class


_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'DObj_has_DAttr', BASE.metadata,
    Column('def_attribute_id', Integer, ForeignKey(
                                          'DEF_Attributes.def_attribute_id')),
    Column('def_object_id', Integer, ForeignKey('DEF_Objects.def_object_id'))
    )


class AttributeHandler(BASE):
  """
  TODO: Description
  """
  def __init__(self):
    pass
  __tablename__ = "AttributeHandlers"
  identifier = Column('AttributeHandler_id', Integer, primary_key=True)
  module_classname = Column('moduleClassName', String)
  description = Column('description', String)
  uuid = Column('uuid', String)
  attributes = relationship('AttributeDefinition', primaryjoin='AttributeHandler.identifier==AttributeDefinition.handler_index')
  ce1sus_id = Column('config', Integer, ForeignKey('ce1sus.ce1sus_id'))
  configuration = relationship('Ce1susConfig')
  __config = None

  @property
  def config(self):
    if self.__config is None:
      config_str = getattr(self.configuration, 'value')
      self.__config = json.loads(config_str)
    return self.__config

  @property
  def classname(self):
    """
    Returns the classname
    """
    return unicode(self.module_classname).rsplit('.')[1]

  @property
  def module(self):
    """
    Returns the module
    """
    return unicode(self.module_classname).rsplit('.')[0]

  def create_instance(self):
    """
    creates an instantiated object
    """
    clazz = get_class('ce1sus.common.handlers.{0}'.format(self.module), self.classname)
    # instantiate
    handler = clazz(self.config)
    # check if handler base is implemented
    if not isinstance(handler, HandlerBase):
      raise HandlerException(('{0} does not implement '
                              + 'HandlerBase').format(self.module_classname))
    return handler


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
                            back_populates='objects', cascade='all',
                            order_by="AttributeDefinition.name")
  dbchksum = Column('chksum', String)
  share = Column('sharable', Integer)

  @property
  def chksum(self):
    return self.dbchksum

  @chksum.setter
  def chksum(self, chksum):
    self.dbchksum = chksum

  def add_attribute(self, attribute):
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

  def remove_attribute(self, attribute):
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


class AttributeDefinition(BASE):
  """This is a container class for the DEF_ATTRIBUTES table."""
  def __init__(self):
    pass

  tableDefinitions = {0: 'TextValue',
                 1: 'StringValue',
                 2: 'DateValue',
                 3: 'NumberValue'}

  __tablename__ = "DEF_Attributes"
  # table class mapping
  identifier = Column('def_attribute_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  regex = Column('regex', String)
  class_index = Column('classIndex', Integer)
  handler_index = Column('handlerIndex', ForeignKey(AttributeHandler.identifier))
  attribute_handler = relationship(AttributeHandler,
                         back_populates='attributes',
                         primaryjoin='AttributeHandler.identifier==AttributeDefinition.handler_index',
                         cascade='all',
                         order_by="AttributeDefinition.name", lazy='joined')
  deletable = Column('deletable', Integer)
  # note class relationTable attribute
  objects = relationship('ObjectDefinition', secondary='DObj_has_DAttr',
                         back_populates='attributes', cascade='all',
                            order_by="ObjectDefinition.name")
  share = Column('sharable', Integer)
  relation = Column('relationable', Integer)
  dbchksum = Column('chksum', String)
  __handler = None

  @property
  def handler(self):
    if self.__handler is None:
      self.__handler = getattr(self.attribute_handler, 'create_instance')()
    return self.__handler

  @property
  def chksum(self):
    return self.dbchksum

  @chksum.setter
  def chksum(self, chksum):
    self.dbchksum = chksum

  @property
  def classname(self):
    """The name for the class used for storing the attribute value"""
    if not self.class_index is None:
      return self.find_classname(self.class_index)
    else:
      return ''

  @staticmethod
  def find_classname(index):
    """
    returns the table name

    :param index: index of the class name
    :type index: Integer

    :returns: String
    """
    # Test if the index is
    if index < 0 and index >= len(AttributeDefinition.tableDefinitions):
      raise Exception('Invalid input "{0}"'.format(index))
    return AttributeDefinition.tableDefinitions[index]

  @staticmethod
  def find_table_index(name):
    """
    searches for the index for the given table name

    :param index: class name
    :type index: String

    :returns: Integer
    """
    result = None
    for index, tablename in AttributeDefinition.tableDefinitions.iteritems():
      if tablename == name:
        result = index
        break
    return result

  @staticmethod
  def get_all_table_names():
    """returns all the table names"""
    result = list()
    for tablename in AttributeDefinition.tableDefinitions.itervalues():
      result.append(tablename)
    return result

  @staticmethod
  def get_cb_values(simple=True):
    """ returns the table definitions where the key is the value and value the
    index of the tables.

    Note: Used for displaying the definitions of the tables in combo boxes

    :returns: Dictionary
    """
    result = dict()
    for index, tablename in AttributeDefinition.tableDefinitions.iteritems():
      if simple:
        key = tablename.replace('Value', '')
      else:
        key = tablename
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
    ObjectValidator.validateDigits(self, 'class_index')
    ObjectValidator.validateDigits(self, 'handler_index')
    return ObjectValidator.isObjectValid(self)

  def add_object(self, obj):
    """
    Add an object to this attribute$

    :param obj: Object to be added
    :type obj: Object
    """
    function = getattr(self.objects, 'append')
    function(obj)

  def remove_object(self, obj):
    """
    Removes an object from this attribute$

    :param obj: Object to be removed
    :type obj: Object
    """
    function = getattr(self.objects, 'remove')
    function(obj)

  @staticmethod
  def is_class_index_existing(index):
    """Returns true if the class index exsits"""
    return index >= 0 and index <= len(AttributeDefinition.tableDefinitions)
