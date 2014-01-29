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

  def getDefintionByCHKSUM(self, chksum):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definition = self.session.query(self.getBrokerClass()).filter(
                                self.getBrokerClass().dbchksum == chksum).one()
      return definition
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No {0} not found for CHKSUM {1}'.format(self.getBrokerClass().__class__.__name__, chksum))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getDefintionByCHKSUMS(self, chksums):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definitions = self.session.query(self.getBrokerClass()).filter(
                              self.getBrokerClass().dbchksum.in_(chksums)).all()
      return definitions
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No {0} not found for CHKSUMS {1}'.format(self.getBrokerClass().__class__.__name__, chksums))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getDefintionByName(self, name):
    """
    Returns the attribute definition object with the given name

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      definition = self.session.query(self.getBrokerClass()).filter(
                                self.getBrokerClass().name == name).one()
      return definition
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for name :{0}'.format(name))
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No {0} not found for {1}'.format(self.getBrokerClass().__class__.__name__, name))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def getAll(self):
    try:
        result = self.session.query(self.getBrokerClass()).order_by(self.getBrokerClass().name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
        raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError, e:
        self.getLogger().fatal(e)
        raise BrokerException(e)
    return result
