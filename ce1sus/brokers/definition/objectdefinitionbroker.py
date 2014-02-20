# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import NothingFoundException, BrokerException, IntegrityException
import sqlalchemy.orm.exc
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, AttributeDefinition
from dagr.helpers.converters import ObjectConverter
from dagr.helpers.hash import hashSHA1
from dagr.helpers.strings import cleanPostValue
from ce1sus.brokers.definition.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.brokers.definition.definitionbase import DefinitionBrokerBase


class ObjectDefinitionBroker(DefinitionBrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    DefinitionBrokerBase.__init__(self, session)
    self.handler_broker = AttributeHandlerBroker(session)
    self.attribute_broker = AttributeDefinitionBroker(session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return ObjectDefinition

  def get_attributes_by_object(self, identifier, belong_in=True):
    """
    returns all attributes belonging to an object with the given identifier

    Note: If nothing is found an empty list is returned

    :param identifier: identifier of the attribute
    :type identifier: Integer
    :param belong_in: If set returns all the objects of the attribute else
                     all the objects not belonging to the attribute
    :type belong_in: Boolean

    :returns: list of AttributeDefinitions
    """
    try:
      attributes = self.session.query(AttributeDefinition).join(
                                          ObjectDefinition.attributes).filter(
                                          ObjectDefinition.identifier ==
                                          identifier).order_by(
                                          AttributeDefinition.name.asc()).all()
      if not belong_in:
        attribute_ids = list()
        for attribute in attributes:
          attribute_ids.append(attribute.identifier)
        attributes = self.session.query(AttributeDefinition).filter(
 ~AttributeDefinition.identifier.in_(attribute_ids)).order_by(
                                          AttributeDefinition.name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return attributes

  def get_cb_values(self):
    """
    returns the values for a combo box where the key is the name of the
    attribute and the value is the identifier.

    :returns: Dictionary
    """
    definitions = self.get_all()
    result = dict()
    for definition in definitions:
      result[definition.name] = (definition.identifier, definition.description)
    return result

  def add_attribute_to_object(self, obj_id, attr_id, commit=True):
    """
    Add an object to an attribute

    :param obj_id: Identifier of the object
    :type obj_id: Integer
    :param attr_id: Identifier of the attribute
    :type attr_id: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == obj_id).one()
      attribute = self.attribute_broker.get_by_id(attr_id)
      obj.add_attribute(attribute)
      additional_attribtues_chksums = attribute.handler.get_additinal_attribute_chksums()
      if additional_attribtues_chksums:
        # collect all required attributes and add them
        additional_attribtues = self.attribute_broker.get_defintion_by_chksums(additional_attribtues_chksums)
        for additional_attribtue in additional_attribtues:
          obj.add_attribute(additional_attribtue)

      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_attribute_from_object(self, obj_id, attr_id, commit=True):
    """
    Removes an object from an attribute

    :param obj_id: Identifier of the object
    :type obj_id: Integer
    :param attr_id: Identifier of the attribute
    :type attr_id: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == obj_id).one()
      attribute = self.attribute_broker.get_by_id(attr_id)
      # check if chksum is not required
      required_chksums = self.attribute_broker.findallchksums(obj)
      # remove self
      existing = required_chksums.get(attribute.chksum, None)
      if existing:
        raise IntegrityException(('Attribute {0} is still required by Object {2} due to Attribute {1}.'
                                  + ' Please remove {1} from Object {2} first.').format(existing[1],
                                                                                        existing[0],
                                                                                        obj.name))
      else:
        obj.remove_attribute(attribute)
        self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  # pylint:disable=R0913
  def build_object_definition(self, identifier=None, name=None,
                  description=None, action='insert',
                               share=None):
    """
    puts an object with the data together

    :param identifier: The identifier of the object,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the object
    :type name: String
    :param description: The description of this object
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: ObjectDefinition
    """
    obj = ObjectDefinition()
    if not action == 'insert':
      obj = self.get_by_id(identifier)
    if not action == 'remove':
      obj.name = cleanPostValue(name)
      obj.description = cleanPostValue(description)
      ObjectConverter.set_integer(obj, 'share', share)
      obj.chksum = hashSHA1(obj.name)
    return obj
