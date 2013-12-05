# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException
import sqlalchemy.orm.exc
from ce1sus.web.helpers.handlers.base import HandlerBase
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, \
                                              AttributeDefinition
from dagr.helpers.converters import ObjectConverter
from dagr.helpers.hash import hashSHA1


class ObjectDefinitionBroker(BrokerBase):
  """This is the interface between python an the database"""
  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return ObjectDefinition

  def getAttributesByObject(self, identifier, belongIn=True):
    """
    returns all attributes belonging to an object with the given identifier

    Note: If nothing is found an empty list is returned

    :param identifier: identifier of the attribute
    :type identifier: Integer
    :param belongIn: If set returns all the objects of the attribute else
                     all the objects not belonging to the attribute
    :type belongIn: Boolean

    :returns: list of AttributeDefinitions
    """
    try:
      attributes = self.session.query(AttributeDefinition).join(
                                          ObjectDefinition.attributes).filter(
                                          ObjectDefinition.identifier ==
                                          identifier).order_by(
                                          AttributeDefinition.name.asc()).all()
      if not belongIn:
        attributeIDs = list()
        for attribute in attributes:
          attributeIDs.append(attribute.identifier)
        attributes = self.session.query(AttributeDefinition).filter(
 ~AttributeDefinition.identifier.in_(attributeIDs)).order_by(
                                          AttributeDefinition.name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return attributes

  def getCBValues(self):
    """
    returns the values for a combo box where the key is the name of the
    attribute and the value is the identifier.

    :returns: Dictionary
    """
    definitions = self.getAll()
    result = dict()
    for definition in definitions:
      result[definition.name] = (definition.identifier, definition.description)
    return result

  def addAttributeToObject(self, attrID, objID, commit=True):
    """
    Add an object to an attribute

    :param objID: Identifier of the object
    :type objID: Integer
    :param attrID: Identifier of the attribute
    :type attrID: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == objID).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attrID).one()
      obj.addAttribute(attribute)
      if not 'GenericHandler' in attribute.handlerName:
        handler = HandlerBase.getHandler(attribute)
        idList = handler.getAttributesIDList()
        # only add attributes if there attributes to be added
        if idList:
          attributes = self.session.query(AttributeDefinition).filter(
                  AttributeDefinition.identifier.in_(idList))
          for attribute in attributes:
            attribute.addObject(obj)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeAttributeFromObject(self, attrID, objID, commit=True):
    """
    Removes an object from an attribute

    :param objID: Identifier of the object
    :type objID: Integer
    :param attrID: Identifier of the attribute
    :type attrID: Integer
    """
    try:
      obj = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.identifier == objID).one()
      attribute = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.identifier == attrID).one()
      obj.removeAttribute(attribute)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getDefintionByCHKSUM(self, chksum):
    """
    Returns the object definition with the given check sum

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param chksum: the chksum of the requested object definition
    :type identifier: integer

    :returns: ObjectDefiniton
    """
    try:
      objectDefinition = self.session.query(ObjectDefinition).filter(
                                ObjectDefinition.dbchksum == chksum).one()
      return objectDefinition
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Object definition not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  @staticmethod
  def buildObjectDefinition(identifier=None, name=None,
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
      obj.identifier = identifier
    if not action == 'remove':
      obj.name = name.strip()
      obj.description = description.strip()
      ObjectConverter.setInteger(obj, 'share', share)
      obj.dbchksum = hashSHA1(obj.name)
    return obj

  def getAll(self):
    """
    Returns all getBrokerClass() instances

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: list of instances
    """
    try:
      result = self.session.query(self.getBrokerClass()
                                  ).order_by(ObjectDefinition.name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result
