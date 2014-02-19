# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import NothingFoundException, \
                           BrokerException, \
                           IntegrityException, DeletionException
from ce1sus.brokers.definition.definitionbase import DefinitionBrokerBase
import sqlalchemy.orm.exc
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, \
                                              AttributeDefinition
from dagr.helpers.converters import ObjectConverter
import dagr.helpers.strings as strings
from dagr.helpers.hash import hashSHA1
from dagr.helpers.strings import cleanPostValue
from ce1sus.brokers.definition.handlerdefinitionbroker import \
                                                        AttributeHandlerBroker


class AttributeDefinitionBroker(DefinitionBrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    DefinitionBrokerBase.__init__(self, session)
    self.handler_broker = AttributeHandlerBroker(session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return AttributeDefinition

  def get_objects_by_attribute(self, identifier, belong_in=True):
    """
    returns all objects belonging to an attribute with the given identifier

    Note: If nothing is found an empty list is returned

    :param identifier: identifier of the object
    :type identifier: Integer
    :param belong_in: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belong_in: Boolean

    :returns: list of ObjectDefinitons
    """
    try:

      objects = self.session.query(ObjectDefinition).join(
                                              AttributeDefinition.objects
                                              ).filter(
                                        AttributeDefinition.identifier ==
                                        identifier).order_by(
                                                    ObjectDefinition.name.asc()
                                                    ).all()
      if not belong_in:
        obj_ids = list()
        for obj in objects:
          obj_ids.append(obj.identifier)
        objects = self.session.query(ObjectDefinition).filter(
 ~ObjectDefinition.identifier.in_(obj_ids)).order_by(ObjectDefinition.name.asc()
                                                    ).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return objects

  def get_cb_values_for_all(self):
    """
    Returns all the values the combobox can use
    """
    definitions = self.get_all()
    result = dict()
    for definition in definitions:
      if definition.name != 'File':
        result[definition.name] = (definition.identifier,
                                   definition.description)
    return result

  def get_cb_values(self, obj_identifier):
    """
    returns the values for a combo box where the key is the name of the
    attribute and the value is the identifier.

    :returns: Dictionary
    """
    definitions = list()
    try:
      definitions = self.session.query(AttributeDefinition).join(
                                              AttributeDefinition.objects
                                              ).filter(
                                        ObjectDefinition.identifier ==
                                        obj_identifier).order_by(
                                        AttributeDefinition.name).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    result = dict()
    for definition in definitions:
      result[definition.name] = (definition.identifier, definition.description)
    return result

  def add_object_to_attribute(self, attr_id, obj_id, commit=True):
    """
    Add an attribute to an object

    :param obj_id: Identifier of the object
    :type obj_id: Integer
    :param attr_id: Identifier of the attribute
    :type attr_id: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == obj_id).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attr_id).one()
      attribute.add_object(obj)
      additional_attribtues_chksums = attribute.handler.get_additinal_attribute_chksums()
      if additional_attribtues_chksums:
        # collect all required attributes and add them
        additional_attribtues = self.get_defintion_by_chksums(additional_attribtues_chksums)
        for additional_attribtue in additional_attribtues:
          obj.add_attribute(additional_attribtue)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound as error:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def _findallchksums(self, obj):
    result = dict()
    for attribute in obj.attributes:
      chksums = attribute.handler.get_additinal_attribute_chksums()
      if chksums:
        if isinstance(chksums, list):
          for chksum in chksums:
            ref_attribute = self.get_defintion_by_chksum(chksum)
            result[chksum] = (attribute.name, ref_attribute.name)
        else:
          attribute = self.get_defintion_by_chksum(chksums)
          result[chksums] = (attribute.name, ref_attribute.name)
    return result

  def remove_object_from_attribute(self, attr_id, obj_id, commit=True):
    """
    Removes an attribute from an object

    :param obj_id: Identifier of the object
    :type obj_id: Integer
    :param attr_id: Identifier of the attribute
    :type attr_id: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == obj_id).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attr_id).one()
      # check if chksum is not required
      required_chksums = self._findallchksums(obj)
      # remove self
      existing = required_chksums.get(attribute.chksum, None)
      if existing:
        raise IntegrityException(('Attribute {0} is still required by attribute {1}.'
                                  + ' Please remove {1} first.').format(existing[1], existing[0]))
      else:
        attribute.remove_object(obj)
        self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_by_id(self, identifier, commit=True):
    """
    Removes the <<get_broker_class()>> with the given identifier

    :param identifier:  the id of the requested user object
    :type identifier: integer
    """
    try:
      self.session.query(AttributeDefinition).filter(AttributeDefinition.
                                            identifier == identifier,
                                            AttributeDefinition.deletable == 1
                      ).delete(synchronize_session='fetch')
    except sqlalchemy.exc.OperationalError as error:
      self.session.rollback()
      raise IntegrityException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    self.do_commit(commit)

  # pylint: disable=R0913
  def build_attribute_definition(self,
                               identifier=None,
                               name=None,
                               description='',
                               regex='^.*$',
                               class_index=0,
                               action='insert',
                               handler_index=1,
                               share=None,
                               relation=None):
    """
    puts an attribute with the data together

    :param identifier: The identifier of the attribute,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the attribute
    :type name: strings
    :param description: The description of this attribute
    :type description: strings
    :param regex: The regular expression to use to verify if the value is
                  correct
    :type regex: strings
    :param class_index: The index of the table to use for storing or getting the
                       attribute actual value
    :type class_index: strings
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: strings

    :returns: AttributeDefinition
    """
    attribute = AttributeDefinition()
    if not action == 'insert':
      attribute = self.get_by_id(identifier)
      if attribute.deletable == 0:
        raise DeletionException('Attribute cannot be edited or deleted')
    if not action == 'remove':
      if isinstance(name, list):
        name = name[0]
      attribute.name = cleanPostValue(name)
      attribute.description = cleanPostValue(description)
      ObjectConverter.set_integer(attribute, 'class_index', class_index)
      ObjectConverter.set_integer(attribute, 'handler_index', handler_index)
      ObjectConverter.set_integer(attribute, 'relation', relation)
      handler = self.handler_broker.get_by_id(attribute.handler_index)
      key = '{0}{1}{2}{3}'.format(attribute.name,
                             attribute.regex,
                             attribute.class_index,
                             handler.uuid)
      attribute.dbchksum = hashSHA1(key)
      trimmed_regex = cleanPostValue(regex)
      if strings.isNotNull(trimmed_regex):
        attribute.regex = trimmed_regex
      else:
        attribute.regex = '^.*$'
      ObjectConverter.set_integer(attribute, 'share', share)
    if action == 'insert':
      attribute.deletable = 1
    return attribute
