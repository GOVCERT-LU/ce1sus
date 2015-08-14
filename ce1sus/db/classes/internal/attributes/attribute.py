# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from ce1sus.helpers.common.objects import get_class
from ce1sus.helpers.common.validator.objectvalidator import FailedValidation, ObjectValidator
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.schema import Table
from sqlalchemy.types import Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.attributes.values import StringValue, DateValue, TextValue, NumberValue
from ce1sus.db.classes.internal.core import BaseElement, SimpleLogingInformations, BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.definitions import AttributeDefinition
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_ATTRIBUTE_CONDITIONS = Table('rel_attribute_conditions', getattr(Base, 'metadata'),
                                  Column('condition_id', BigIntegerType, ForeignKey('conditions.condition_id', ondelete='cascade', onupdate='cascade'), primary_key=True, nullable=False, index=True),
                                  Column('attribute_id', BigIntegerType, ForeignKey('attributes.attribute_id', ondelete='cascade', onupdate='cascade'), primary_key=True, nullable=False, index=True)
                                  )

class Condition(SimpleLogingInformations, Base):
  value = Column('value', UnicodeType(40), unique=True)
  description = Column('description', UnicodeTextType())

  _PARENTS = ['attribute']

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'value': self.convert_value(self.value),
            'description': self.convert_value(self.description),
            }

  def validate(self):
    # TODO validate
    return True


class Attribute(BaseElement, Base):
  description = Column('description', UnicodeTextType())

  definition_id = Column('definition_id', BigIntegerType,
                         ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(AttributeDefinition,
                            primaryjoin='AttributeDefinition.identifier==Attribute.definition_id',
                            lazy='joined')
  object_id = Column('object_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  object = relationship('Object',
                        primaryjoin='Object.identifier==Attribute.object_id',
                        lazy='joined')
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
  condition_id = Column('condition_id', BigIntegerType, ForeignKey('conditions.condition_id', ondelete='restrict', onupdate='restrict'), index=True, default=None)
  condition = relationship(Condition, uselist=False, secondary=_REL_ATTRIBUTE_CONDITIONS, backref='attribute')

  _PARENTS = ['object']

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
      try:
        value_table = self.definition.value_table
      except AttributeError as error:
        raise error
      classname = '{0}Value'.format(value_table)
      attribute = '{0}_value'.format(value_table.lower())

      # check if not a value has been assigned
      value_instance = self.__get_value_instance()
      if value_instance:
        # update only
        value_instance.value = new_value
      else:
        value_instance = get_class('ce1sus.db.classes.internal.attributes.values', classname)
        value_instance = value_instance()
        value_instance.attribute_id = self.identifier
        value_instance.attribute = self
        value_instance.value = new_value
        value_instance.value_type_id = self.definition.value_type_id

      if self.object:
        if self.object.event or self.object.event_id:
          event_id = self.object.event_id
          if event_id:
            value_instance.event_id = event_id
          else:
            event = self.object.event
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

  @property
  def value_instance(self):
    return self.__get_value_instance()

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

  def to_dict(self, cache_object):
    condition = None
    condition_id = None
    if self.condition:
      condition = self.condition.to_dict(cache_object)
      condition_id = self.convert_value(self.condition.uuid)

    value = self.convert_value(self.value)
    handler_uuid = '{0}'.format(self.definition.attribute_handler.uuid)
    if handler_uuid in ['0be5e1a0-8dec-11e3-baa8-0800200c9a66', 'e8b47b60-8deb-11e3-baa8-0800200c9a66']:
      # serve file
      fh = self.definition.handler

      filepath = fh.get_base_path() + '/' + value
      # TODO: Find a way not to do this aways
      # with open(filepath, "rb") as raw_file:
      #    value = b64encode(raw_file.read())

    result = {'identifier': self.convert_value(self.uuid),
            'definition_id': self.convert_value(self.definition.uuid),
            'definition': self.definition.to_dict(cache_object),
            'ioc': self.is_ioc,
            'value': value,
            'condition_id': condition_id,
            'condition': condition,
            }
    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
