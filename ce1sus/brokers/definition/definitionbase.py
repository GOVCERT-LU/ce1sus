# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 28, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException, TooManyResultsFoundException
import sqlalchemy.orm.exc


class DefinitionBrokerBase(BrokerBase):
  """This is the interface between python an the database"""

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_defintion_by_chksum(self, chksum):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definition = self.session.query(self.get_broker_class()).filter(
                                self.get_broker_class().dbchksum == chksum).one()
      return definition
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No {0} not found for CHKSUM {1}'.format(self.get_broker_class().__class__.__name__, chksum))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self._get_logger().fatal(error)
      self.session.rollback()
      raise BrokerException(error)

  def get_defintion_by_chksums(self, chksums):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definitions = self.session.query(self.get_broker_class()).filter(
                              self.get_broker_class().dbchksum.in_(chksums)).all()
      return definitions
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No {0} not found for CHKSUMS {1}'.format(self.get_broker_class().__class__.__name__, chksums))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self._get_logger().fatal(error)
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
      definition = self.session.query(self.get_broker_class()).filter(
                                self.get_broker_class().name == name).one()
      return definition
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for name :{0}'.format(name))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No {0} not found for {1}'.format(self.get_broker_class().__class__.__name__, name))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self._get_logger().fatal(error)
      self.session.rollback()
      raise BrokerException(error)

  def get_all(self):
    try:
        result = self.session.query(self.get_broker_class()).order_by(self.get_broker_class().name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
        self._get_logger().fatal(error)
        raise BrokerException(error)
    return result
