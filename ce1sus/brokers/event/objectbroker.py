# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, \
                           BrokerException
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_
from dagr.helpers.datumzait import datumzait
from ce1sus.brokers.event.eventclasses import Object
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.helpers.bitdecoder import BitValue
from dagr.helpers.converters import ObjectConverter


class ObjectBroker(BrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attributeBroker = AttributeBroker(session)

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Object

  def removeByID(self, identifier, commit=True):
    """
    overrides BrokerBase.removeByID
    """
    try:
      obj = self.getByID(identifier)
      # check if objects does not have children
      children = self.getChildOjectsForObjectID(obj.identifier)
      if len(children) > 0:
        raise BrokerException('Object has children. '
                + 'The object cannot be removed if there are still children.')
      else:
        # remove attributes
        self.attributeBroker.removeAttributeList(obj.attributes, False)
        self.doCommit(False)
        BrokerBase.removeByID(self, obj.identifier, False)
        self.doCommit(commit)
    except BrokerException as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  @staticmethod
  def buildObject(identifier,
                  event,
                  definition,
                  user,
                  parentObjectID=None,
                  shared=0):
    """
    puts an object together

    :param identifier: ID of the object
    :type identifier: Ineger
    :param event: event which the object belongs to
    :type event: Event
    :param definition: Definition of the object
    :type definition: ObjectDefinition
    :param user: User performing the action
    :type user: User

    :returns: Object
    """
    obj = Object()
    obj.identifier = identifier
    obj.definition = definition
    if not definition is None:
      obj.def_object_id = definition.identifier
    obj.created = datumzait.utcnow()
    if not event is None:
      eventID = event.identifier
    else:
      eventID = None
    if parentObjectID is None:

      obj.event_id = eventID
    else:
      obj.parentObject_id = parentObjectID
      obj.parentEvent_id = eventID

    obj.creator_id = user.identifier
    ObjectConverter.setInteger(obj, 'shared', shared)
    obj.bitValue = BitValue('1000', obj)
    return obj

  def getCDValuesObjectParents(self, eventID, notObject):
    """
    Returns all the child objects of the objects for a given event

    :returns: List of Objects
    """
    try:
      # first level

      result = self.session.query(Object).filter(
                                            or_(
                                              Object.parentEvent_id == eventID,
                                              Object.event_id == eventID
                                               ),
                                              Object.identifier != notObject
                                                          )
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                  eventID))

  def getChildObjectsForEvent(self, eventID):
    """
    Returns all the child objects of the objects for a given event

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(Object.parentEvent_id
                                                 == eventID).all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                  eventID))

  def getViewableChildObjectsForEvent(self, eventID):
    """
    Returns all the child objects of the objects for a given event

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(Object.parentEvent_id
                                                 == eventID,
                                                Object.dbcode.op('&')(12) == 12
                                                 )
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                  eventID))

  def getChildOjectsForObjectID(self, objectID):
    """
    Returns all the child objects of the given object

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(
                        Object.parentObject_id == objectID).all()
      for obj in result:
        subChildren = self.getChildOjectsForObjectID(obj.identifier)
        if not subChildren is None:
          result = result + subChildren
      return result
    except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                  objectID))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

  def getObjectsOfEvent(self, eventID):
    try:
      # first level
      result = self.session.query(Object).filter(Object.event_id
                                                 == eventID
                                                 )
      return result.all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
        return list()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

  def getViewableOfEvent(self, eventID):
    try:
      # first level
      result = self.session.query(Object).filter(Object.event_id
                                                 == eventID,
                                                Object.dbcode.op('&')(12) == 12
                                                 )
      return result.all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
        return list()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)
