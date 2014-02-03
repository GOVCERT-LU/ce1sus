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
  return System.APP_REL


class System(object):

  APP_REL = '1.0.0'
  DB_REL = '0.7.0'
  REST_REL = '2.0.0'

  def __init__(self, config):
    self.config = config
    self.connector = SessionManager(config).connector
    self.ce1sus_broker = Ce1susBroker(self.connector.get_direct_session())

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
        result = -1
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
    result = System.compareValues(array1[0], array2[0])
    if result >= 0:
      result = System.compareValues(array1[1], array2[1])
      if result >= 0:
        result = System.compareValues(array1[2], array2[2])
        if result >= 0:
          return 0
    return result

  def check_db(self):
    try:
      value = self.ce1sus_broker.get_by_key('db_shema')
      if System.compareReleases(System.DB_REL, value.value) != 0:
        raise SantityCheckerException('DB scheme release mismatch '
                          + 'expected {0} got {1}'.format(System.DB_REL,
                                                         value.value))
    except BrokerException as error:
      raise SystemException(error)

  def __check_ce1sus(self):
    # check app rel
    try:
      value = self.ce1sus_broker.get_by_key('app_rev')
      if System.compareReleases(System.APP_REL,
                                        value.value) != 0:
        raise SantityCheckerException('Application release mismatch '
                          + 'expected {0} got {1}'.format(System.APP_REL,
                                                         value.value))
    except BrokerException as error:
      raise SystemException(error)

  def check_rest_api(self, release):
    try:
    # check app rel
      value = self.ce1sus_broker.get_by_key('rest_api')
      if System.compareReleases(release,
                                        value.value) != 0:
        raise SantityCheckerException('RestAPI release mismatch '
                          + 'expected {1} got {1}'.format(value.value,
                                                        release))
      if System.compareReleases(System.REST_REL,
                                        value.value) != 0:
        raise SantityCheckerException('RestAPI release mismatch '
                          + 'expected {1} got {0}'.format(
                                                        value.value,
                                                        release))
    except BrokerException as error:
      raise SystemException(error)

  def update_handler_config(self):
    try:
      section = self.config.get_section('Handlers')
      json_str = json.dumps(section)
      value = self.ce1sus_broker.get_by_key('handler_config')
      value.value = json_str
      self.ce1sus_broker.update(value)
    except BrokerException as error:
      raise SystemException(error)

  def perform_web_checks(self):
    self.check_db()
    self.__check_ce1sus()
    self.update_handler_config()

    self.connector.close()
