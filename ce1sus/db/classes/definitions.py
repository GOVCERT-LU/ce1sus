# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
import json
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, BIGINT, Text, Boolean

from ce1sus.db.classes.base import SimpleLogingInformations
from ce1sus.db.classes.common import ValueTable
from ce1sus.db.common.session import Base
from ce1sus.handlers.base import HandlerBase, HandlerException
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator, FailedValidation


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'objectdefinition_has_attributedefinitions', getattr(Base, 'metadata'),
    Column('oha_id', BIGINT, primary_key=True, nullable=False, index=True),
    Column('attributedefinition_id', BIGINT, ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True),
    Column('objectdefinition_id', BIGINT, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
)


class DefinitionException(Exception):
  pass


class AttributeDefinitionException(DefinitionException):
  pass


class AttributeHandler(SimpleLogingInformations, Base):

  module_classname = Column('moduleClassName', Unicode(255), nullable=False, unique=True, index=True)
  description = Column('description', Text)
  configuration = relationship('Ce1susConfig')
  ce1sus_id = Column('ce1susconfig_id', BIGINT, ForeignKey('ce1susconfigs.ce1susconfig_id', onupdate='restrict', ondelete='restrict'), index=True, nullable=False)
  __config = None

  @property
  def config(self):
    """
    Returns the global configuration for handlers
    """
    if self.__config is None:
      config_str = getattr(self.configuration, 'value')
      self.__config = json.loads(config_str)
    return self.__config

  @property
  def classname(self):
    """
    Returns the class name of the handler
    """
    return self.module_classname.rsplit('.')[1]

  @property
  def module(self):
    """
    Returns the module of the handler
    """
    return self.module_classname.rsplit('.')[0]

  @property
  def clazz(self):
    clazz = get_class('ce1sus.handlers.{0}'.format(self.module), self.classname)
    return clazz

  def create_instance(self):
    """
    creates an instantiated object
    """
    # instantiate
    handler = self.clazz(self.config)
    # check if handler base is implemented
    if not isinstance(handler, HandlerBase):
      raise HandlerException((u'{0} does not implement '
                              + 'HandlerBase').format(self.module_classname))
    return handler

  def validate(self):
    # TODO: Verify validation of AttributeHandler Object
    return True


class ObjectDefinition(SimpleLogingInformations, Base):

  name = Column('name', Unicode(255), nullable=False, unique=True, index=True)
  description = Column('description', Text)
  chksum = Column('chksum', Unicode(255), unique=True, nullable=False, index=True)
  default_share = Column('sharable', Boolean, default=False, nullable=False)
  default_operator = Column('default_operator', Integer, default=0, nullable=False)

  possible_attributes = relationship('AttributeDefinition',
                                     secondary='objectdefinition_has_attributedefinitions',
                                     backref='objects',
                                     order_by='AttributeDefinition.name')
  # TOOD: find a way to make a subset from possible_attributes
  # TODO: Add administration of minimal objects -> checked before publishing
  required_attributes = relationship('AttributeDefinition',
                                     secondary='objectdefinition_has_attributedefinitions',
                                     backref='objects',
                                     order_by='AttributeDefinition.name')

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Verify validation of ObjectDefinition Object
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


class AttributeDefinition(SimpleLogingInformations, Base):

  name = Column('name', Unicode(45), unique=True, nullable=False, index=True)
  description = Column('description', Text)
  chksum = Column('chksum', Unicode(45), unique=True, nullable=False, index=True)
  regex = Column('regex', Unicode(255), unique=True, nullable=False, default='^.+$')
  table_id = Column('table_id', Integer, nullable=False, default=0)
  attributehandler_id = Column('attributehandler_id', ForeignKey(AttributeHandler.identifier, onupdate='restrict', ondelete='restrict'), index=True)
  deletable = Column('deletable', Boolean, default=True, nullable=False)
  share = Column('sharable', Boolean, default=False, nullable=False)
  # TODO: make an event on relationable to recreate and remove the relations on change
  relation = Column('relationable', Boolean, default=False, nullable=False)
  __handler = None

  @property
  def handler(self):
    """
    Returns the instantiatied handler
    """
    if self.__handler is None:
      self.__handler = getattr(self.attribute_handler, 'create_instance')()
    return self.__handler

  @property
  def value_table(self):
    """The name for the class used for storing the attribute value"""
    if self.table_id is None:
      raise AttributeDefinitionException(u'No table was defined for {0}'.format(self.__class__.__name__))
    else:
      value = None
      if isinstance(self.table_id, FailedValidation):
        value = self.table_id.value
      else:
        value = self.table_id

      return ValueTable.get_by_id(value)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Verify validation of AttributeDefinition Object
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
    ObjectValidator.validateDigits(self, 'table_id')
    ObjectValidator.validateDigits(self, 'attributehandler_id')
    # check if handler is compatible with the class_index
    allowed_classes = self.handler.get_allowed_types()
    if not (self.class_index in allowed_classes):
      class_index = self.class_index
      self.class_index = FailedValidation(class_index,
                                          ('Class is not compatible "{0}".\n'
                                           'Supported classes are {1}').format(self.attribute_handler.classname,
                                                                               self.__class_numbers_to_text(allowed_classes))
                                          )

    return ObjectValidator.isObjectValid(self)
