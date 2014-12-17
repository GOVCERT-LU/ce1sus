# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""
import sqlalchemy.orm.exc
from sqlalchemy.sql.expression import or_, and_, not_, distinct

from ce1sus.db.classes.event import Event
from ce1sus.db.classes.observables import Observable
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, \
  TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class ObservableBroker(BrokerBase):
  """
  This broker handles all operations on event objects
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Observable

  def get_by_id_and_event_id(self, identifier, event_id):
    try:
      result = self.session.query(Observable).filter(and_(Observable.identifier == identifier, Observable.event_id == event_id)).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No observable found with ID :{0} in event with ID {1}'.format(identifier, event_id))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for observable with ID {0} in event with ID {1}'.format(identifier, event_id))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result
