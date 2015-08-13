# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from ce1sus.helpers.common.debug import Log


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ChangeLogger(object):

  def __init__(self, config=None):
    log = Log(config)
    self.__logger = log.get_logger('ChangeLogger')

  def error(self, message):
    self.__logger.error(message)

  def warning(self, message):
    self.__logger.warning(message)

  def debug(self, message):
    self.__logger.debug(message)

  def info(self, message):
    self.__logger.info(message)

  def critical(self, message):
    self.__logger.critical(message)
