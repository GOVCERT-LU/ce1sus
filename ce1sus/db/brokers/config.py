# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 2, 2014
"""
import sqlalchemy.orm.exc

from ce1sus.db.classes.internal.backend.config import Ce1susConfig
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susConfigBroker(BrokerBase):
  """This is the interface between python an the database"""

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Ce1susConfig

  def get_by_key(self, key):
    """
    Returns a Ce1susConfig by it's key
    """
    try:
      return self.session.query(Ce1susConfig).filter(Ce1susConfig.key == key).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with key :{0}'.format(key))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for key :{0}'.format(key))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
