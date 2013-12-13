# -*- coding: utf-8 -*-

"""
Module providing support for the configuration of web applications

Created: Oct 1st, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.session import BASE
from sqlalchemy import Column, String
import sqlalchemy.orm
from dagr.db.session import SessionManager
from dagr.helpers.debug import Log


class SantityCheckerException(Exception):
  """SantityCheckerException"""
  def __init__(self, message):
    Exception.__init__(self, message)


# pylint: disable=R0903
class SanityValue(BASE):
  __tablename__ = "ce1sus"
  key = Column('key', String, primary_key=True)
  value = Column('value', String)


class SantityChecker(object):

  APP_REL = '0.4.5'
  DB_REL = '0.4.0'
  REST_REL = '0.2.0'

  def __init__(self, configFile):
    # setup connection string and engine
    self.sessionHandler = SessionManager(configFile, createInstance=False)
    self.session = self.sessionHandler.connector.getDirectSession()

  def getBrokerClass(self):
    return SanityValue

  def checkDB(self):
    # check db rel
    value = self.getByKey('db_shema')
    if SantityChecker.compareReleases(SantityChecker.DB_REL, value.value) != 0:
      raise SantityCheckerException('DB scheme release mismatch '
                        + 'expected {0} got {1}'.format(SantityChecker.DB_REL,
                                                       value.value))

  def checkApplication(self):
    # check app rel
    value = self.getByKey('app_rev')
    if SantityChecker.compareReleases(SantityChecker.APP_REL,
                                      value.value) != 0:
      raise SantityCheckerException('Application release mismatch '
                        + 'expected {0} got {1}'.format(SantityChecker.APP_REL,
                                                       value.value))

  def checkRestAPI(self, release):
    # check app rel
    value = self.getByKey('rest_api')
    if SantityChecker.compareReleases(release,
                                      value.value) != 0:
      raise SantityCheckerException('RestAPI release mismatch '
                        + 'expected {1} got {1}'.format(value.value,
                                                      release))
    if SantityChecker.compareReleases(SantityChecker.REST_REL,
                                      value.value) != 0:
      raise SantityCheckerException('RestAPI release mismatch '
                        + 'expected {1} got {0}'.format(
                                                      value.value,
                                                      release))

  def close(self):
    self.session.close()
    self.sessionHandler.close()

  def getByKey(self, key):
    """
    Returns the object by the given identifier

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:
      result = self.session.query(SanityValue).filter(
                        SanityValue.key == key).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise SantityCheckerException('Nothing found with ID :{0}'.format(
                                                                  key))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise SantityCheckerException(
                    'Too many results found for ID :{0}'.format(key))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise SantityCheckerException(e)

    return result

  @staticmethod
  def compareValues(value1, value2):
    """
    Compares the releases

    :param value1: A release under the form of X.X.X
    :type value1: String
    :param value2: A release under the form of X.X.X
    :type value2: String

    returns:
        1 if value 1 > value 2
        0 if value 1 = value 2
        -1 if value 1 < value 2
    """
    isNumber = True
    try:
      value1 = int(value1)
      value2 = int(value2)
    except ValueError:
      isNumber = False

    if value1 == value2:
      result = 0
    else:
      if isNumber:
        if value1 - value2 > 0:
          result = 1
        else:
          result = -1
      else:
        result = 1
    return result

  @staticmethod
  def compareReleases(release1, release2):
    """
    Compares the releases

    :param release1: A release under the form of X.X.X
    :type release1: String
    :param release2: A release under the form of X.X.X
    :type release2: String

    returns:
        1 if rel 1 > rel 2
        0 if rel 1 = rel 2
        -1 if rel 1 < rel 2

    """
    array1 = release1.split('.')
    array2 = release2.split('.')

    if len(array1) != len(array2) and len(array1) != 3:
      raise SantityCheckerException('The releases have not the right format.')
    result = SantityChecker.compareValues(array1[0], array2[0])
    if result == 0:
      result = SantityChecker.compareValues(array1[1], array2[1])
      if result == 0:
        result = SantityChecker.compareValues(array1[2], array2[2])
        if result >= 0:
          return 0
    return result

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)


def version(context):
  return SantityChecker.APP_REL
