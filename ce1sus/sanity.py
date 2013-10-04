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
from dagr.helpers.config import Configuration
from dagr.db.session import SessionManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dagr.db.recepie.satool import ForeignKeysListener
import os

class SantityCheckerException(Exception):
  """SantityCheckerException"""
  def __init__(self, message):
    Exception.__init__(self, message)

class SanityValue(BASE):
  __tablename__ = "ce1sus"
  key = Column('key', String, primary_key=True)
  value = Column('value', String)

class SantityChecker(object):

  APP_REL = '0.A.0'
  DB_REL = '0.A.0'

  def __init__(self, configFile):
    # load __config foo!!
    self.__config = Configuration(configFile, 'SessionManager')
    # setup connection string and engine
    protocol = self.__config.get('protocol')
    debug = self.__config.get('debug')
    if debug == None:
      debug = False
    if (protocol == 'sqlite'):
      connetionString = '{prot}:///../../../{db}'.format(prot=protocol,
                                                  db=self.__config.get('db'))
      self.sa_engine = create_engine(connetionString,
                            listeners=[ForeignKeysListener()],
                            echo=debug, echo_pool=debug)
    else:
      hostname = self.__config.get('host')
      port = self.__config.get('port')
      # check if host is available
      response = os.system("ping -c 1 " + hostname)
      if response != 0:
        raise SantityCheckerException('Host "{hostname}" not ' +
                                      'available'.format(hostname=hostname))
      # check if socket available
      if not SessionManager.isServiceExisting(hostname, port):
        raise SantityCheckerException('Service on "{hostname}:{port}"' +
                                      ' not available'.format(hostname=hostname,
                                                               port=port))
      connetionString = '{prot}://{user}:{password}@{host}:{port}/{db}'.format(
        prot=protocol,
        user=self.__config.get('username'),
        password=self.__config.get('password'),
        host=hostname,
        db=self.__config.get('db'),
        port=port
      )
      self.sa_engine = create_engine(connetionString,
                            echo=debug, echo_pool=debug)
      Session = sessionmaker(bind=self.sa_engine)
      self.session = Session()

  def getBrokerClass(self):
    return SanityValue

  def check(self):
    # check app rel
    value = self.getByKey('app_rev')
    if SantityChecker.compareReleases(SantityChecker.APP_REL, value.value) != 0:
      raise SantityCheckerException('Application release mismatch '
                        + 'expected {0} got {1}'.format(SantityChecker.APP_REL,
                                                       value.value))
    # check db rel
    value = self.getByKey('db_shema')
    if SantityChecker.compareReleases(SantityChecker.DB_REL, value.value) != 0:
      raise SantityCheckerException('DB scheme release mismatch '
                        + 'expected {0} got {1}'.format(SantityChecker.DB_REL,
                                                       value.value))
    self.__close()

  def __close(self):
    self.sa_engine.dispose()
    self.sa_engine = None

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
    if result >= 0:
      result = SantityChecker.compareValues(array1[1], array2[1])
      if result >= 0:
        result = SantityChecker.compareValues(array1[2], array2[2])
        if result >= 0:
          return 0
    return result

def version(context):
  return SantityChecker.APP_REL
