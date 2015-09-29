# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

from ce1sus.helpers.common.objects import get_class
import sqlalchemy
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import func

from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.attributes.values import VALUE_TABLES
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.classes.internal.report import Reference, ReferenceDefinition
from ce1sus.db.common.broker import BrokerBase, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class SearchBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return None

  def set_operator(self, query, clazz, attribute_name_list, needle, operator, insensitive):



    # query = query.join(condition_class.path)
    if insensitive:
      needle = needle.lower()

    conditions = list()
    for attribute_name in attribute_name_list:
      if hasattr(clazz, attribute_name):
        attr = getattr(clazz, attribute_name)
        if insensitive:
          attr = func.lower(attr)

        if operator == '==':
          conditions.append(attr == needle)
        elif operator == '<':
          conditions.append(attr < needle)
        elif operator == '>':
          conditions.append(attr > needle)
        elif operator == '<=':
          conditions.append(attr <= needle)
        elif operator == '>=':
          conditions.append(attr >= needle)
        elif operator == 'like':
          conditions.append(attr.like('%{0}%'.format(needle)))
        elif operator == 'in':
          if isinstance(needle, list):
            conditions.append(attr.in_(needle))
          else:
            raise BrokerException('needle is not a list')
        else:
          raise BrokerException('Operator not defined')

    if conditions:
        return query.filter(
                            *conditions
                            )
    else:
      raise Exception('No conditions could be generated')

  def __get_values(self, found_values, bypass_validation):
    result = list()
    for found_value in found_values:
      if bypass_validation:
        result.append(found_value)
      else:
        if found_value.properties.is_validated:
          result.append(found_value)
    return result

  def look_for_value_by_properties(self, clazz, property_names, needle, operator, insensitive, bypass_validation=False):
    try:
      query = self.session.query(clazz)
      query = self.set_operator(query, clazz, property_names, needle, operator, insensitive)
      found_values = query.all()
      return self.__get_values(found_values, bypass_validation)
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def look_for_value_by_property_name(self, clazz, property_name, needle, operator, insensitive, bypass_validation=False):
    return self.look_for_value_by_properties(clazz, [property_name], needle, operator, insensitive, bypass_validation)
    
  def look_for_descriptions(self, clazz, needle, operator, insensitive, bypass_validation=False):
    """
    Searches the tables for a value
    """
    try:
      found_values = list()
      basequery = self.session.query(clazz.identifier)
      basequery = self.set_operator(basequery, StructuredText, ['value'], needle, operator, insensitive)
      if hasattr(clazz, 'description'):
        query = basequery.join(clazz.description)
        result = query.all()
        found_values.extend(result)
      if hasattr(clazz, 'short_description'):
        query = basequery.join(clazz.short_description)
        result = query.all()
        found_values.extend(result)
      result = list()
      for value in found_values:
        result.append(value[0])
      return self.__check_code(clazz, result, bypass_validation)
      
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def __query_attribute_value(self, clazz, needle, operator, insensitive):
    query = self.session.query(clazz.attribute_id)
    query = self.set_operator(query, clazz, ['value'], needle, operator, insensitive)
    # query = query.options(joinedload(Attribute.value_base), joinedload(Attribute.path))
    values = query.all()
    result = list()
    for value in values:
      result.append(value[0])
    return result

  def __get_options(self, clazz):
    options = [
               joinedload(clazz.path),
               joinedload(clazz.path).joinedload(Path.event),
               joinedload(clazz.path).joinedload(Path.event).joinedload(Event.stix_header),
               joinedload(clazz.path).joinedload(Path.event).joinedload(Event.stix_header).joinedload(STIXHeader.path),
               joinedload(clazz.path).joinedload(Path.event).joinedload(Event.path)
               ]
    return options

  def __check_code(self,clazz, ids, bypass_validation=False):
    if ids:
      options = self.__get_options(clazz)
      if clazz.get_classname() == 'Attribute':
        query = self.session.query(Attribute).options(joinedload(Attribute.value_base),
                                                      joinedload(Attribute.definition),
                                                      *options
                                                      ).filter(Attribute.identifier.in_(ids))
      elif clazz.get_classname() == 'Reference':
        query = self.session.query(Reference).options(
                                                      joinedload(Reference.definition),
                                                      joinedload(Reference.definition).joinedload(ReferenceDefinition.reference_handler),
                                                      *options
                                                      ).filter(Reference.identifier.in_(ids))
      elif clazz.get_classname() == 'Object':
        query = self.session.query(Object).options(
                                                      joinedload(Object.definition),
                                                      *options
                                                      ).filter(Object.identifier.in_(ids))
      else:
        query = self.session.query(clazz).options(*options).filter(clazz.identifier.in_(ids))
      found_values = query.all()
    else:
      found_values = list()
    return self.__get_values(found_values, bypass_validation)

  def look_for_attribute_value(self, definition, needle, operator, insensitive, bypass_validation=False):
    try:

      if definition:
        clazz = get_class('ce1sus.db.classes.internal.attributes.values', '{0}Value'.format(definition.value_table))
        result = self.__query_attribute_value(clazz, needle, operator, insensitive)
        result = self.__check_code(Attribute, result, bypass_validation=bypass_validation)
        return result
      else:
        result = list()
        for clazz in VALUE_TABLES:
          items = self.__query_attribute_value(clazz, needle, operator, insensitive)
          items = self.__check_code(Attribute, items, bypass_validation=bypass_validation)
          result.extend(items)
        return result
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def look_for_reference_value(self, definition_name, needle, operator, insensitive, bypass_validation=False):
    try:
      query = self.session.query(Reference.identifier)
      if definition_name:
        query = query.join(Reference.definition).filter(ReferenceDefinition.name == definition_name)

      query = self.set_operator(query, Reference, ['value'], needle, operator, insensitive)
      values = query.all()
      result = list()
      for value in values:
        result.append(value[0])
      result = self.__check_code(Reference, result, bypass_validation=bypass_validation)
      return result

    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
