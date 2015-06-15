# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 6, 2014
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from ce1sus.db.classes.attribute import Condition
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ConditionBroker(BrokerBase):

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Condition

  def get_condition_by_value(self, value):
    try:
      if value == None:
        value = 'Equals'
      return self.session.query(Condition).filter(Condition.value == value).one()
    except NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0} in {1}'.format(value, self.__class__.__name__))
    except MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(value))
    except SQLAlchemyError as error:
      raise BrokerException(error)
