# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 2, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException
from dagr.db.session import BASE
from sqlalchemy import Column, Integer, String
import sqlalchemy.orm.exc
from dagr.helpers.datumzait import datumzait
from ce1sus.brokers.event.eventclasses import Comment
from dagr.helpers.strings import cleanPostValue


# pylint: disable=R0903,R0902
class Ce1susConfig(BASE):
  __tablename__ = 'ce1sus'
  identifier = Column('ce1sus_id', Integer, primary_key=True)
  key = Column('key', String)
  value = Column('value', String)

  def validate(self):
    """
    Returns true if the object is valid
    """
    return self


class Ce1susBroker(BrokerBase):
  """This is the interface between python an the database"""
  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Ce1susConfig

  def get_by_key(self, key):
    try:
      return self.session.query(Ce1susConfig).filter(Ce1susConfig.key == key).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with key :{0}'.format(
                                                                  key))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for key :{0}'.format(key))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
