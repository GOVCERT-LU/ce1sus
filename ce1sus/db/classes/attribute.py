# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, UnicodeText, Boolean, Unicode

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.db.classes.values import StringValue, DateValue, TextValue, NumberValue
from ce1sus.db.common.session import Base
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import FailedValidation, ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_ATTRIBUTE_CONDITIONS = Table('rel_attribute_conditions', Base.metadata,
                                  Column('condition_id', Unicode(40), ForeignKey('conditions.condition_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                  Column('attribute_id', Unicode(40), ForeignKey('attributes.attribute_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                  )


class Condition(Base):
  value = Column('value', Unicode(40))


class Attribute(ExtendedLogingInformations, Base):
  description = Column('description', UnicodeText)

  definition_id = Column('definition_id', Unicode(40),
                         ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(AttributeDefinition,
                            primaryjoin='AttributeDefinition.identifier==Attribute.definition_id')
  object_id = Column('object_id', Unicode(40), ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  object = relationship('Object',
                        primaryjoin='Object.identifier==Attribute.object_id')
  # valuerelations
  string_value = relationship(StringValue,
                              primaryjoin='Attribute.identifier==StringValue.attribute_id',
                              lazy='joined', uselist=False)
  date_value = relationship(DateValue,
                            primaryjoin='Attribute.identifier==DateValue.attribute_id',
                            uselist=False, lazy='joined')
  text_value = relationship(TextValue,
                            primaryjoin='Attribute.identifier==TextValue.attribute_id',
                            uselist=False, lazy='joined')
  number_value = relationship(NumberValue,
                              primaryjoin='Attribute.identifier==NumberValue.attribute_id',
                              uselist=False, lazy='joined')
  is_ioc = Column('is_ioc', Boolean)
  # TODO make relation table
  condition = relationship('Condition', uselist=False, secondary='rel_attribute_conditions', lazy='joined')
  parent_id = Column('parent_id', Unicode(40), ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='SET NULL'), index=True, default=None)
  children = relationship('Attribute',
                          primaryjoin='Attribute.identifier==Attribute.parent_id')
  dbcode = Column('code', Integer)
  __bit_code = None

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code

  def __get_value_instance(self):
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
    if self.definition:
      value_table = self.definition.value_table
      classname = '{0}Value'.format(value_table)
      attribute = '{0}_value'.format(value_table.lower())

      value_instance = get_class('ce1sus.db.classes.values', classname)
      value_instance = value_instance()
      value_instance.attribute_id = self.identifier
      value_instance.attribute = self
      value_instance.value = new_value
      value_instance.value_type_id = self.definition.value_type_id

      if self.object:
        if self.object.parent:
          event_id = self.object.parent.event_id
          if event_id:
            value_instance.event_id = event_id
          else:
            event = self.object.parent.event
            if event:
              value_instance.event = event
            else:
              raise ValueError(u'Cannot set the attribute value as the event for of the parent object is not yet set.')
        else:
          raise ValueError(u'Parent of object was not set.')
      else:
        raise ValueError(u'Cannot set the attribute value as the parent object is not yet set.')

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

  def to_dict(self, complete=True, inflated=False):
    condition = None
    if self.condition:
      condition = self.condition.value

    return {'identifier': self.convert_value(self.identifier),
            'definition': self.definition.to_dict(complete, inflated),
            'shared': self.properties.is_shareable,
            'ioc': self.is_ioc,
            'value': self.convert_value(self.value),
            'condition': self.convert_value(condition),
            'creator_group': self.creator_group.to_dict(complete, inflated),
            'created_at': self.convert_value(self.created_at),
            'modified_on': self.convert_value(self.modified_on),
            'modifier_group': self.convert_value(self.modifier.group.to_dict(complete, inflated)),
            }
