# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 6, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from dagr.db.session import SessionManager
from ce1sus.brokers.ce1susbroker import Ce1susBroker
from dagr.db.broker import BrokerException
import json


# The releases are formated as A.B.C where A,B,C are defined as follows
# A: Major Release
# B: Release feature changes
# C: Bug fixes/Small features
APP_REL = '0.8.16'
DB_REL = '0.8.3'
REST_REL = '0.2.0'


# pylint: disable=W0613
def sytem_version(context):
  """
  Just for displaing inside the leyout
  """
  return APP_REL


class SystemException(Exception):
  """SantityCheckerException"""
  pass


class SantityCheckerException(SystemException):
  """SantityCheckerException"""
  pass


class System(object):
  """
  System class
  """

  def __init__(self, config):
    self.config = config
    self.connector = SessionManager(config).connector
    self.ce1sus_broker = Ce1susBroker(self.connector.get_direct_session())
    self.handler_config_udated = False

  @staticmethod
  def __compare_values(value1, value2):
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
    is_number = True
    try:
      value1 = int(value1)
      value2 = int(value2)
    except ValueError:
      is_number = False

    if value1 == value2:
      result = 0
    else:
      if is_number:
        if value1 - value2 > 0:
          result = 1
        else:
          result = -1
      else:
        result = -1
    return result

  @staticmethod
  def __compare_releases(release1, release2):
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
      raise SantityCheckerException(u'The releases have not the right format.')
    result = System.__compare_values(array1[0], array2[0])
    if result == 0:
      result = System.__compare_values(array1[1], array2[1])
      if result == 0:
        # Second position means major changes
        result = System.__compare_values(array1[2], array2[2])
        if result >= 0:
          # Third position means new version
          return 0
    return result

  def __check_db(self):
    """
    Checks if the db is compatible with the appliation
    """
    try:
      value = self.ce1sus_broker.get_by_key('db_shema')
      if System.__compare_releases(DB_REL, value.value) != 0:
        raise SantityCheckerException(u'DB scheme release mismatch '
                          + 'expected {0} got {1}'.format(DB_REL,
                                                         value.value))
    except BrokerException as error:
      raise SystemException(error)

  def __check_ce1sus(self):
    """
    Checks if the application is compatible with the db
    """
    # check app rel
    try:
      value = self.ce1sus_broker.get_by_key('app_rev')
      if System.__compare_releases(APP_REL,
                                        value.value) != 0:
        raise SantityCheckerException(u'Application release mismatch '
                          + 'expected {0} got {1}'.format(APP_REL,
                                                         value.value))
    except BrokerException as error:
      raise SystemException(error)

  @staticmethod
  def check_rest_api(release):
    """
    Checks if the rest api is compatible
    """
    try:
      # check app rel
      if System.__compare_releases(REST_REL, release) != 0:
        raise SantityCheckerException(u'RestAPI release mismatch '
                          + 'expected {1} got {0}'.format(REST_REL,
                                                          release))
    except BrokerException as error:
      raise SystemException(error)

  def __update_handler_config(self):
    """
    updates the configuration for the handlers
    """
    try:
      section = self.config.get_section('Handlers')
      json_str = json.dumps(section)
      value = self.ce1sus_broker.get_by_key('handler_config')
      value.value = json_str
      self.ce1sus_broker.update(value)
    except BrokerException as error:
      raise SystemException(error)

  def __global_checks(self):
    """
    Compilation of checks valid everywhere
    """
    self.__check_db()
    if not self.handler_config_udated:
      self.handler_config_udated = True
      self.__update_handler_config()

  def perform_web_checks(self):
    """
    Required checks for the web front end
    """
    self.__global_checks()
    self.__check_ce1sus()

  def perform_rest_api_startup_checks(self):
    """
    Rest api startup checks
    """
    self.__global_checks()

  def close(self):
    """
    Close system
    """
    self.connector.close()
