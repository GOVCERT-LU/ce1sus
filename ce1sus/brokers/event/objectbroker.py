# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_
from dagr.helpers.datumzait import DatumZait
from ce1sus.brokers.event.eventclasses import Object
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.helpers.bitdecoder import BitValue
import uuid as uuidgen


class ObjectBroker(BrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.attribute_broker = AttributeBroker(session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Object

  def remove_by_id(self, identifier, commit=True):
    """
    overrides BrokerBase.remove_by_id
    """
    try:
      obj = self.get_by_id(identifier)
      # check if objects does not have children
      children = self.get_object_childern_for_obj_id(obj.identifier)
      if len(children) > 0:
        raise BrokerException(u'Object has children. '
                + 'The object cannot be removed if there are still children.')
      else:
        BrokerBase.remove_by_id(self, obj.identifier, False)
        self.do_commit(commit)
    except BrokerException as error:
      self.session.rollback()
      raise BrokerException(error)

  @staticmethod
  def build_object(identifier,
                  event_id,
                  definition,
                  user,
                  parent_object_id=None,
                  shared=0,
                  action='insert'):
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
    if action == 'insert':
      obj.uuid = unicode(uuidgen.uuid4())
    else:
      obj.identifier = identifier

    if action != 'remove':
      obj.definition = definition
      if not definition is None:
        obj.def_object_id = definition.identifier
    obj.created = DatumZait.utcnow()
    if parent_object_id is None:
      obj.event_id = event_id
    else:
      obj.parent_object_id = parent_object_id
      obj.parent_event_id = event_id
    obj.creator_id = user.identifier
    obj.modified = DatumZait.utcnow()
    obj.bit_value = BitValue('0', obj)
    if shared == '1':
      obj.bit_value.is_shareable = True
    else:
      obj.bit_value.is_shareable = False
    return obj

  def get_cb_values_object_parents(self, event_id, object_id):
    """
    Returns all the child objects of the objects for a given event in the cb format

    :returns: List of Objects
    """
    try:
      result = self.session.query(Object).filter(
                                            or_(
                                              Object.parent_event_id == event_id,
                                              Object.event_id == event_id
                                               ),
                                              Object.identifier != object_id
                                                          )
      objs = result.all()

      values = dict()
      for obj in objs:
        key = '{0} - {1}'.format(obj.definition.name, obj.identifier)
        values[key] = obj.identifier
      return values
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with ID :{0}'.format(
                                                                  event_id))

  def get_event_objects_children(self, event_id):
    """
    Returns all the child objects of the objects for a given event

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(Object.parent_event_id
                                                 == event_id).all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with ID :{0}'.format(
                                                                  event_id))

  def get_viewable_event_obj_children(self, event_id):
    """
    Returns all the child objects of the objects for a given event

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(Object.parent_event_id
                                                 == event_id,
                                                Object.dbcode.op('&')(12) == 12
                                                 )
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with ID :{0}'.format(
                                                                  event_id))

  def get_object_childern_for_obj_id(self, object_id):
    """
    Returns all the child objects of the given object

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(
                        Object.parent_object_id == object_id).all()
      for obj in result:
        sub_children = self.get_object_childern_for_obj_id(obj.identifier)
        if not sub_children is None:
          result = result + sub_children
      return result
    except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException(u'Nothing found with ID :{0}'.format(
                                                                  object_id))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_event_objects(self, event_id):
    """
    Returns the objects of the event

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(Object.event_id
                                                 == event_id
                                                 )
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
        return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_event_objects(self, event_id):
    """
    Return all the objects belonging to an event even the object children
    """
    try:
      result = self.session.query(Object).filter(or_(Object.event_id == event_id,
                                                     Object.parent_event_id == event_id)
                                                 )
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
        return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_viewable_event_objects(self, event_id):
    """
    Returns the objects of the event

    :returns: List of Objects
    """
    try:
      # first level
      result = self.session.query(Object).filter(Object.event_id
                                                 == event_id,
                                                Object.dbcode.op('&')(12) == 12
                                                 )
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
        return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def update_object(self, user, obj, commit=True):
    """
    updates an object

    If it is invalid the event is returned

    :param event:
    :type event: Event
    """
    obj.modifier = user
    obj.modified = DatumZait.utcnow()
    self.update(obj, False)
    self.do_commit(commit)
