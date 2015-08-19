# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
import sqlalchemy.orm.exc

from ce1sus.db.brokers.definitions.definitionbase import DefinitionBrokerBase
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.classes.internal.definitions import AttributeDefinition, ObjectDefinition
from ce1sus.db.common.broker import NothingFoundException, BrokerException, IntegrityException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeDefinitionBroker(DefinitionBrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    super(AttributeDefinitionBroker, self).__init__(session)
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

      objects = self.session.query(ObjectDefinition).join(AttributeDefinition.objects).filter(AttributeDefinition.identifier == identifier).order_by(ObjectDefinition.name.asc()).all()
      if not belong_in:
        obj_ids = list()
        for obj in objects:
          obj_ids.append(obj.identifier)
        objects = self.session.query(ObjectDefinition).filter(~ObjectDefinition.identifier.in_(obj_ids)).order_by(ObjectDefinition.name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found for ID: {0}',
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

  def add_object_to_attribute(self, attr_id, obj_id, commit=True):
    """
    Add an attribute to an object

    :param obj_id: Identifier of the object
    :type obj_id: Integer
    :param attr_id: Identifier of the attribute
    :type attr_id: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(ObjectDefinition.identifier == obj_id).one()
      attribute = self.session.query(AttributeDefinition).filter(AttributeDefinition.identifier == attr_id).one()
      attribute.add_object(obj)
      additional_attributes_chksums = attribute.handler.get_additinal_attribute_chksums()
      if additional_attributes_chksums:
        # collect all required attributes and add them
        additional_attributes = self.get_defintion_by_chksums(additional_attributes_chksums)
        for additional_attribute in additional_attributes:
          obj.add_attribute(additional_attribute)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound as error:
      raise NothingFoundException(u'Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_object_from_attribute(self, attr_id, obj_id, commit=True):
    """
    Removes an attribute from an object

    :param obj_id: Identifier of the object
    :type obj_id: Integer
    :param attr_id: Identifier of the attribute
    :type attr_id: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(ObjectDefinition.identifier == obj_id).one()
      attribute = self.session.query(AttributeDefinition).filter(AttributeDefinition.identifier == attr_id).one()
      # check if chksum is not required
      required_chksums = self.findallchksums(obj)
      # remove self
      existing = required_chksums.get(attribute.chksum, None)
      if existing:
        raise IntegrityException((u'Attribute {0} is still required by attribute {1}.'
                                  + ' Please remove {1} first.').format(existing[1], existing[0]))
      else:
        attribute.remove_object(obj)
        self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Attribute or Object not found')
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
      self.session.query(AttributeDefinition).filter(AttributeDefinition.identifier == identifier,
                                                     AttributeDefinition.cybox_std is False
                                                     ).delete(synchronize_session='fetch')
    except sqlalchemy.exc.OperationalError as error:
      self.session.rollback()
      raise IntegrityException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    self.do_commit(commit)

  def get_all_relationable_definitions(self):
    try:
      definitions = self.session.query(AttributeDefinition).filter(AttributeDefinition.relation == 1).all()
      if definitions:
        return definitions
      else:
        raise sqlalchemy.orm.exc.NoResultFound
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'No {0} is set as relationable'.format(self.get_broker_class().__class__.__name__))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
