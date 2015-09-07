# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator, FailedValidation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer, Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.attributes.attribute import Condition
from ce1sus.db.classes.internal.backend.types import AttributeType
from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.db.classes.internal.core import SimpleLoggingInformations
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType, BaseObject
from ce1sus.db.common.session import Base
from ce1sus.handlers.base import HandlerBase, HandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'objectdefinition_has_attributedefinitions', getattr(Base, 'metadata'),
    Column('oha_id', BigIntegerType, primary_key=True, nullable=False, index=True),
    Column('attributedefinition_id', BigIntegerType, ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True),
    Column('objectdefinition_id', BigIntegerType, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
)


class DefinitionException(Exception):
  pass


class AttributeDefinitionException(DefinitionException):
  pass


class ObjectDefinition(SimpleLoggingInformations, Base):

  name = Column('name', UnicodeType(255), nullable=False, unique=True, index=True)
  description = Column('description', UnicodeTextType())
  chksum = Column('chksum', UnicodeType(255), unique=True, nullable=False, index=True)
  default_share = Column('sharable', Boolean, default=False, nullable=False)

  # the relationship is flagged with true when it is a required attribute
  attributes = relationship('AttributeDefinition',
                            secondary='objectdefinition_has_attributedefinitions',
                            order_by='AttributeDefinition.name')
  cybox_std = Column('cybox_std', Boolean, default=False)

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

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description),
              'chksum': self.convert_value(self.chksum),
              'default_share': self.convert_value(self.default_share),
              'attributes': self.attributelist_to_dict('attributes', cache_object),
              'cybox_std': self.convert_value(self.cybox_std)
              }
    else:
      result = {
              'name': self.convert_value(self.name),
              'chksum': self.convert_value(self.chksum),
              'cybox_std': self.convert_value(self.cybox_std)
              }

    parent_dict = SimpleLoggingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)



class AttributeDefinition(SimpleLoggingInformations, Base):

  name = Column('name', UnicodeType(45), unique=True, nullable=False, index=True)
  description = Column('description', UnicodeTextType())
  chksum = Column('chksum', UnicodeType(45), unique=True, nullable=False, index=True)
  regex = Column('regex', UnicodeType(255), nullable=False, default=u'^.+$')
  table_id = Column('table_id', Integer, nullable=False, default=0)
  attributehandler_id = Column('attributehandler_id', BigIntegerType, ForeignKey('attributehandlers.attributehandler_id', onupdate='restrict', ondelete='restrict'), index=True, nullable=False)
  attribute_handler = relationship('AttributeHandler',
                                   primaryjoin='AttributeHandler.identifier==AttributeDefinition.attributehandler_id',
                                   cascade='all'
                                   )
  share = Column('sharable', Boolean, default=False, nullable=False)
  # TODO: make an event on relationable to recreate and remove the relations on change
  relation = Column('relationable', Boolean, default=False, nullable=False)
  value_type_id = Column('attributetype_id', BigIntegerType, ForeignKey('attributetypes.attributetype_id'))
  value_type = relationship(AttributeType, uselist=False)
  objects = relationship('ObjectDefinition',
                         secondary='objectdefinition_has_attributedefinitions',
                         order_by='ObjectDefinition.name')
  default_condition_id = Column('default_condition_id', BigIntegerType, ForeignKey('conditions.condition_id', onupdate='restrict', ondelete='restrict'), index=True, nullable=False)
  default_condition = relationship(Condition, uselist=False,)
  __handler = None
  cybox_std = Column('cybox_std', Boolean, default=False)

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

    # check if handler is compatible with the class_index
    allowed_tables = self.handler.get_allowed_types()
    if not (self.table_id in allowed_tables):
      self.class_index = FailedValidation(self.table_id,
                                          ('Class is not compatible "{0}".\n'
                                           'Supported classes are {1}').format(self.attribute_handler.classname,
                                                                               self.__class_numbers_to_text(allowed_tables))
                                          )
    return ObjectValidator.isObjectValid(self)

  @staticmethod
  def __class_numbers_to_text(class_array):
    # TODO: Tables classes to text
    return u'{0}'.format(class_array)


  def to_dict(self, cache_object):
    instance = self.get_instance(True)
    if cache_object.complete:
      result = {
              'name': instance.convert_value(instance.name),
              'description': instance.convert_value(instance.description),
              'attributehandler_id': instance.convert_value(instance.attribute_handler.uuid),
              'attributehandler': instance.handler.to_dict(),
              'table_id': instance.convert_value(instance.table_id),
              'relation': instance.convert_value(instance.relation),
              'share': instance.convert_value(instance.share),
              'regex': instance.convert_value(instance.regex),
              'type_id': instance.convert_value(instance.value_type.uuid),
              'default_condition_id': instance.convert_value(instance.default_condition.uuid),
              'chksum': instance.convert_value(instance.chksum),
              'cybox_std': instance.convert_value(instance.cybox_std)
              }
    else:
      result = {
              'name': instance.convert_value(instance.name),
              'default_condition_id': instance.convert_value(instance.default_condition.uuid),
              'chksum': instance.convert_value(instance.chksum),
              'cybox_std': instance.convert_value(instance.cybox_std)
              }

    parent_dict = SimpleLoggingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class AttributeHandler(BaseObject, Base):

  module_classname = Column('moduleClassName', UnicodeType(255), nullable=False, unique=True, index=True)
  description = Column('description', UnicodeTextType(), nullable=False)

  @property
  def classname(self):
    """
    Returns the class name of the handler
    """
    return self.module_classname.rsplit('.', 1)[1]

  @property
  def module(self):
    """
    Returns the module of the handler
    """
    return self.module_classname.rsplit('.', 1)[0]

  @property
  def clazz(self):
    clazz = get_class('ce1sus.handlers.attributes.{0}'.format(self.module), self.classname)
    return clazz

  def create_instance(self):
    """
    creates an instantiated object
    """
    # instantiate
    handler = self.clazz()
    # check if handler base is implemented
    if not isinstance(handler, HandlerBase):
      raise HandlerException((u'{0} does not implement '
                              + 'HandlerBase').format(self.module_classname))
    return handler

  def validate(self):
    # TODO: Verify validation of AttributeHandler Object
    return True

  def to_dict(self, cache_object):
    result = list()
    handler = self.create_instance()
    allowed_tables = handler.get_allowed_types()
    for allowed_table in allowed_tables:
      name = ValueTable.get_by_id(allowed_table)
      result.append({'identifier': allowed_table, 'name': name})
    result = {'description': self.convert_value(self.description),
            'name': self.convert_value(self.classname),
            'identifier': self.convert_value(self.uuid),
            'allowed_tables': result
            }
    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
