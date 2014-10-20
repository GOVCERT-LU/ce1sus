# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Text, Boolean, BIGINT

from ce1sus.db.classes.base import ExtendedLogingInformations
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.db.classes.values import StringValue, DateValue, TextValue, NumberValue
from ce1sus.db.common.session import Base
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import FailedValidation, ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Attribute(ExtendedLogingInformations, Base):
  description = Column('description', Text)

  definition_id = Column('definition_id', BIGINT,
                         ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(AttributeDefinition,
                            primaryjoin='AttributeDefinition.identifier==' +
                            'Attribute.def_attribute_id')
  object_id = Column('object_id', BIGINT, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  object = relationship('Object',
                        primaryjoin='Object.identifier==Attribute.object_id')
  # valuerelations
  string_value = relationship(StringValue,
                              primaryjoin='Attribute.identifier==StringValue.attribute_id',
                              lazy='joined', uselist=False)
  date_value = relationship(DateValue,
                            primaryjoin='Attribute.identifier==DateValue.attribute_id',
                            uselist=False)
  text_value = relationship(TextValue,
                            primaryjoin='Attribute.identifier==TextValue.attribute_id',
                            uselist=False)
  number_value = relationship(NumberValue,
                              primaryjoin='Attribute.identifier==NumberValue.attribute_id',
                              uselist=False)
  type_id = Column('type_id', Integer)
  is_ioc = Column('is_ioc', Boolean)
  parent_id = Column('parent_id', BIGINT, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='SET NULL'), index=True, default=None)
  children = relationship('Attribute',
                          primaryjoin='Attribute.identifier==Attribute.parent_id')

  def __is_composed(self):
    if self.rel_composition:
      raise ValueError(u'Attribute is composed')

  def __get_value_instance(self):
    self.__is_composed()
    """
    Returns the value object of an attibute
    """
    if self.string_value:
      value = self.string_value
    elif self.date_value:
      value = self.date_value
    elif self.text_value:
      value = self.text_value
    elif self.number_value:
      value = self.number_value
    else:
      value = None
    return value

  def __get_value(self):
    self.__is_composed()
    """
    Returns the actual value of an attribute
    """
    value_instance = self.__get_value_instance()
    # check if the value instance is set
    if value_instance:
      # if the value is not valid
      if isinstance(value_instance, FailedValidation):
        # if the validation has failed return the failed object
        value = value_instance
      else:
        # else return the value of the instance
        value = value_instance.value
      return value
    else:
      return None

  def __set_value(self, new_value):
    self.__is_composed()
    if self.definition:
      value_table = self.definition.value_table
      classname = value_table.classname
      attribute = value_table.attribute

      value_instance = get_class('ce1sus.db.classes.values', classname)()
      value_instance.attribute_id = self.identifier
      value_instance.attribute = self
      value_instance.value = new_value

      setattr(self, attribute, value_instance)

    else:
      raise ValueError(u'Cannot set the attribute value as the definition is not yet set.')

  @property
  def value(self):
    return self.__get_value()

  @value.setter
  def value(self, value):
    self.__set_value(value)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateDigits(self, 'def_attribute_id')
    # validate attribute value
    value_instance = self.__get_value_instance()
    # TODO: encoding error
    ObjectValidator.validateRegex(value_instance,
                                  'value',
                                  getattr(self.definition, 'regex'),
                                  u'The value "{0}" does not match {1} for definition {2}'.format(value_instance.value,
                                                                                                  getattr(self.definition, 'regex'),
                                                                                                  getattr(self.definition, 'name')).encode('utf-8'),
                                  True)
    if not isinstance(value_instance, FailedValidation):
      errors = not getattr(value_instance, 'validate')()
      if errors:
        return False
    return ObjectValidator.isObjectValid(self)
