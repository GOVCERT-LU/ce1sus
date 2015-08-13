# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 23, 2014
"""

import sqlalchemy.orm.exc
from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class RelatedObjectBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return RelatedObject

  def get_parent_object_by_object_id(self, identifier):
    try:
      return self.session.query(Object).join(RelatedObject, RelatedObject.parent_id == Object.identifier).filter(RelatedObject.child_id == identifier).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(identifier, self.__class__.__name__))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_related_object_by_child_object_id(self, identifier):
    try:
      return self.session.query(RelatedObject).filter(RelatedObject.child_id == identifier).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(identifier, self.__class__.__name__))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
