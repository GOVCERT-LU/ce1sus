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
                           TooManyResultsFoundException, \
BrokerException
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_
from dagr.helpers.datumzait import datumzait
from ce1sus.brokers.event.eventclasses import ObjectAttributeRelation, \
                                              Object
from ce1sus.brokers.event.attributebroker import AttributeBroker
from sqlalchemy.orm import joinedload_all
from ce1sus.helpers.bitdecoder import BitValue
from dagr.helpers.converters import ObjectConverter
from dagr.helpers.string import cleanPostValue


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

  def getRelationsByObjectIDList(self, objectIDList):
    """
    returns the relations by the object id

    :param objectID: obect identifier
    :type objectID: Integer

    :returns: List of ObjectAttributeRelation
    """
    if len(objectIDList) == 0:
      return list()
    try:
      result = self.session.query(
                              ObjectAttributeRelation
                            ).join(
                                   ObjectAttributeRelation.sameAttribute
                                  ).options(
                                        joinedload_all(
                                         ObjectAttributeRelation.sameAttribute
                                                       )
                                           ).filter(
                                    ObjectAttributeRelation.ref_object_id.in_(
                                                                  objectIDList
                                                                            ),
                        # only object wich are validated and shared are shown
                        Object.dbcode.op('&')(12) == 12
                        ).all()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                objectIDList))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for ID :{0}'.format(objectIDList))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

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
      obj.def_object_id = obj.definition.identifier
    obj.created = datumzait.utcnow()
    if event is None:
      obj.event = None
      obj.event_id = None
    else:
      obj.event = event
      obj.event_id = obj.event.identifier
    if parentObjectID is None:
      obj.parentObject_id = None
    else:
      obj.parentObject_id = parentObjectID
    obj.creator = user
    obj.creator_id = obj.creator.identifier
    ObjectConverter.setInteger(obj, 'shared', shared)
    obj.bitValue = BitValue('1001', obj)
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
