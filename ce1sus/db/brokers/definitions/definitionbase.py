# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 28, 2014
"""
import sqlalchemy.orm.exc

from ce1sus.db.common.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DefinitionBrokerBase(BrokerBase):
  """This is the interface between python an the database"""

  def get_defintion_by_chksum(self, chksum):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definition = self.session.query(self.get_broker_class()).filter(getattr(self.get_broker_class(), 'chksum') == chksum).one()
      return definition
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'No {0} not found for CHKSUM {1}'.format(self.get_broker_class().__class__.__name__,
                                                                            chksum))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def get_defintion_by_name(self, name):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definition = self.session.query(self.get_broker_class()).filter(getattr(self.get_broker_class(), 'name') == name).one()
      return definition
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for name :{0}'.format(name))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'No {0} not found for {1}'.format(self.get_broker_class().__class__.__name__, name))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
