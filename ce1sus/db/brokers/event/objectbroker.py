# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy.orm.exc

from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class ObjectBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Object

  def get_parent_object_by_object(self, obj):
    try:
      result = self.session.query(RelatedObject).filter(RelatedObject.child_id == obj.identifier).one()
      return result.parent
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No parent found for object with ID {0} in {1}'.format(obj.identifier, self.__class__.__name__))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all_by_observable_id(self, identifier):
    try:

      result = self.session.query(Object).filter(Object.observable_id == identifier).all()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(identifier, self.__class__.__name__))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
