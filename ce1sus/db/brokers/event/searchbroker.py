# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 31, 2014
"""

from ce1sus.helpers.common.objects import get_class
import sqlalchemy
from sqlalchemy.sql.expression import and_, or_

from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.attributes.values import NumberValue, StringValue, VALUE_TABLES
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

  def set_operator(self, query, clazz, attribute_name_list, needle, operator, bypass_validation=False, condition_class=None):
    if bypass_validation:
      code = 0
    else:
      code = 4
    if not condition_class:
      condition_class = clazz
    
    conditions = list()
    for attribute_name in attribute_name_list:
      if hasattr(clazz, attribute_name):
        if operator == '==':
          conditions.append(getattr(clazz, attribute_name) == needle)
        elif operator == '<':
          conditions.append(getattr(clazz, attribute_name) < needle)
        elif operator == '>':
          conditions.append(getattr(clazz, attribute_name) > needle)
        elif operator == '<=':
          conditions.append(getattr(clazz, attribute_name) <= needle)
        elif operator == '>=':
          conditions.append(getattr(clazz, attribute_name) >= needle)
        elif operator == 'like':
          conditions.append(getattr(clazz, attribute_name).like('%{0}%'.format(needle)))
        else:
          raise Exception('Operator not defined')

    if len(conditions) == 1:
      return query.filter(condition_class.dbcode.op('&')(code) == code,
                          *conditions
                          )
    elif len(conditions) > 1:
      return query.filter(and_(condition_class.dbcode.op('&')(code) == code,
                               or_(*conditions)
                               )
                          )
    else:
      raise Exception('No conditions could be generated')

  def look_for_value_by_properties(self, clazz, property_name, needle, operator, bypass_validation=False):
    try:
      query = self.session.query(clazz)
      query = self.set_operator(query, clazz, property_name, needle, operator, bypass_validation)
      return query.all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def look_for_value_by_property_name(self, clazz, property_name, needle, operator, bypass_validation=False):
    try:
      query = self.session.query(clazz)
      query = self.set_operator(query, clazz, [property_name], needle, operator, bypass_validation)
      return query.all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
    
  def look_for_descriptions(self, clazz, needle, operator, bypass_validation=False):
    """
    Searches the tables for a value
    """
    try:
      found_values = list()
      basequery = self.session.query(StructuredText)
      basequery = self.set_operator(basequery, StructuredText, ['value'], needle, operator, bypass_validation)
      if hasattr(clazz, 'description'):
        query = basequery.join(clazz.description)
        result = query.all()
        found_values.extend(result)
      if hasattr(clazz, 'short_description'):
        query = basequery.join(clazz.short_description)
        result = query.all()
        found_values.extend(result)
      return found_values
      
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def look_for_attribute_value(self, definition, needle, operator, bypass_validation=False):
    try:
      query = self.session.query(Attribute).join(Attribute.value_base)
      if definition:
        clazz = get_class('ce1sus.db.classes.internal.attributes.values', '{0}Value'.format(definition.value_table))
        query = self.set_operator(query, clazz, ['value'], needle, operator, condition_class=Attribute)
        return query.all()
      else:
        result = list()
        for clazz in VALUE_TABLES:
          query = self.set_operator(query, clazz, ['value'], needle, operator, condition_class=Attribute)
          result.extend(query.all())
        return result
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def look_for_reference_value(self, definition_name, needle, operator, bypass_validation=False):
    try:
      query = self.session.query(Reference)
      if definition_name:
        query = query.join(Reference.definition).filter(ReferenceDefinition.name == definition_name)

      query = self.set_operator(query, Reference, ['value'], needle, operator, bypass_validation)
      return query.all()

    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
