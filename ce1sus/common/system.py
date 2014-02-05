# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 2, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from dagr.db.session import SessionManager
from ce1sus.brokers.system.ce1susbroker import Ce1susBroker
from dagr.db.broker import BrokerException
import json

# The releases are formated as A.B.C where A,B,C are defined as follows
# A: Major Release
# B: Release feature changes
# C: Bug fixes
APP_REL = '0.7.0'
DB_REL = '0.8.0'
REST_REL = '0.2.0'


class SystemException(Exception):
  """SantityCheckerException"""
  pass


class SantityCheckerException(SystemException):
  """SantityCheckerException"""
  pass


def sytem_version(context):
  """
  Just for displaing inside the leyout
  """
  return APP_REL


class System(object):

  def __init__(self, config):
    self.config = config
    self.connector = SessionManager(config).connector
    self.ce1sus_broker = Ce1susBroker(self.connector.get_direct_session())
    self.handler_config_udated = False

  @staticmethod
  def __compareValues(value1, value2):
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
        result = -1
    return result

  @staticmethod
  def __compareReleases(release1, release2):
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
    result = System.__compareValues(array1[0], array2[0])
    if result >= 0:
      result = System.__compareValues(array1[1], array2[1])
      if result >= 0:
        result = System.__compareValues(array1[2], array2[2])
        if result >= 0:
          return 0
    return result

  def __check_db(self):
    try:
      value = self.ce1sus_broker.get_by_key('db_shema')
      if System.__compareReleases(DB_REL, value.value) != 0:
        raise SantityCheckerException('DB scheme release mismatch '
                          + 'expected {0} got {1}'.format(DB_REL,
                                                         value.value))
    except BrokerException as error:
      raise SystemException(error)

  def __check_ce1sus(self):
    # check app rel
    try:
      value = self.ce1sus_broker.get_by_key('app_rev')
      if System.__compareReleases(APP_REL,
                                        value.value) != 0:
        raise SantityCheckerException('Application release mismatch '
                          + 'expected {0} got {1}'.format(APP_REL,
                                                         value.value))
    except BrokerException as error:
      raise SystemException(error)

  @staticmethod
  def check_rest_api(release):
    try:
      # check app rel
      if System.__compareReleases(REST_REL, release) != 0:
        raise SantityCheckerException('RestAPI release mismatch '
                          + 'expected {1} got {0}'.format(REST_REL,
                                                          release))
    except BrokerException as error:
      raise SystemException(error)

  def __update_handler_config(self):
    try:
      section = self.config.get_section('Handlers')
      json_str = json.dumps(section)
      value = self.ce1sus_broker.get_by_key('handler_config')
      value.value = json_str
      self.ce1sus_broker.update(value)
    except BrokerException as error:
      raise SystemException(error)

  def __global_checks(self):
    self.__check_db()
    if not self.handler_config_udated:
      self.handler_config_udated = True
      self.__update_handler_config()

  def perform_web_checks(self):
    self.__global_checks()
    self.__check_ce1sus()

  def perform_rest_api_startup_checks(self):
    self.__global_checks()

  def close(self):
    self.connector.close()

