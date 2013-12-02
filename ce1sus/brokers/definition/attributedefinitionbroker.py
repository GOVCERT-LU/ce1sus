# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 5, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, \
                           BrokerException, \
                           OperationException, DeletionException
import sqlalchemy.orm.exc
from ce1sus.web.helpers.handlers.base import HandlerBase
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, \
                                              AttributeDefinition
from dagr.helpers.converters import ObjectConverter
import dagr.helpers.string as string
from dagr.helpers.hash import hashSHA1


class AttributeDefinitionBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return AttributeDefinition

  def getObjectsByAttribute(self, identifier, belongIn=True):
    """
    returns all objects belonging to an attribute with the given identifier

    Note: If nothing is found an empty list is returned

    :param identifier: identifier of the object
    :type identifier: Integer
    :param belongIn: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belongIn: Boolean

    :returns: list of ObjectDefinitons
    """
    try:

      objects = self.session.query(ObjectDefinition).join(
                                              AttributeDefinition.objects
                                              ).filter(
                                        AttributeDefinition.identifier ==
                                        identifier).all()
      if not belongIn:
        objIDs = list()
        for obj in objects:
          objIDs.append(obj.identifier)
        objects = self.session.query(ObjectDefinition).filter(
 ~ObjectDefinition.identifier.in_(objIDs))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found for ID: {0}',
                                  format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    return objects

  def getCBValuesForAll(self):
    """
    Returns all the values the combobox can use
    """
    definitions = self.getAll()
    result = dict()
    for definition in definitions:
      if definition.name != 'File':
        result[definition.name] = (definition.identifier,
                                   definition.description)
    return result

  def getCBValues(self, objIdentifier):
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
                                        objIdentifier).order_by(
                                        AttributeDefinition.name).all()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().debug(e)
      self.session.rollback()
      raise BrokerException(e)

    result = dict()
    for definition in definitions:
      result[definition.name] = (definition.identifier, definition.description)
    return result

  def addObjectToAttribute(self, objID, attrID, commit=True):
    """
    Add an attribute to an object

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
      attribute.addObject(obj)
      if not 'GenericHandler' in attribute.handlerName:
        handler = HandlerBase.getHandler(attribute)
        try:
          nameList = handler.getAttributesNameList()
        except TypeError:
          nameList = list()
        attributes = self.session.query(AttributeDefinition).filter(
                AttributeDefinition.name.in_(nameList))
        for attribute in attributes:
          attribute.addObject(obj)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound as e:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeObjectFromAttribute(self, objID, attrID, commit=True):
    """
    Removes an attribute from an object

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
      attribute.removeObject(obj)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute or Object not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getDefintionByName(self, name):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      attributeDefinition = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.name == name).one()
      return attributeDefinition
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute definition not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getDefintionByCHKSUM(self, chksum):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      attributeDefinition = self.session.query(AttributeDefinition).filter(
                                AttributeDefinition.dbchksum == chksum).one()
      return attributeDefinition
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Attribute definition not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeByID(self, identifier, commit=True):
    """
    Removes the <<getBrokerClass()>> with the given identifier

    :param identifier:  the id of the requested user object
    :type identifier: integer
    """
    try:
      self.session.query(AttributeDefinition).filter(AttributeDefinition.
                                            identifier == identifier,
                                            AttributeDefinition.deletable == 1
                      ).delete(synchronize_session='fetch')
    except sqlalchemy.exc.OperationalError as e:
      self.session.rollback()
      raise OperationException(e)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

    self.doCommit(commit)

  # pylint: disable=R0913
  def buildAttributeDefinition(self,
                               identifier=None,
                               name=None,
                               description='',
                               regex='^.*$',
                               classIndex=0,
                               action='insert',
                               handlerIndex=0,
                               share=None,
                               relation=None):
    """
    puts an attribute with the data together

    :param identifier: The identifier of the attribute,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the attribute
    :type name: String
    :param description: The description of this attribute
    :type description: String
    :param regex: The regular expression to use to verify if the value is
                  correct
    :type regex: String
    :param classIndex: The index of the table to use for storing or getting the
                       attribute actual value
    :type classIndex: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: AttributeDefinition
    """
    attribute = AttributeDefinition()
    if not action == 'insert':
      attribute = self.getByID(identifier)
      if attribute.deletable == 0:
        raise DeletionException('Attribute cannot be edited or deleted')
    if not action == 'remove':
      attribute.name = name.strip()
      attribute.description = description.strip()
    ObjectConverter.setInteger(attribute, 'classIndex', classIndex)
    ObjectConverter.setInteger(attribute, 'handlerIndex', handlerIndex)
    ObjectConverter.setInteger(attribute, 'relation', relation)
    key = '{0}{1}{2}'.format(attribute.name,
                             attribute.regex,
                             attribute.classIndex,
                             attribute.handlerIndex)
    attribute.dbchksum = hashSHA1(key)
    trimmedRegex = regex.strip()
    if string.isNotNull(trimmedRegex):
      attribute.regex = trimmedRegex
    else:
      attribute.regex = '^.*$'
    ObjectConverter.setInteger(attribute, 'share', share)
    if action == 'insert':
      attribute.deletable = 1
    return attribute
