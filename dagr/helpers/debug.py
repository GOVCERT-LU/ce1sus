# -*- coding: utf-8 -*-

"""
Debugging module

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import logging
from dagr.helpers.config import Configuration
from dagr.helpers.string import isNotNull
from logging.handlers import RotatingFileHandler


class Log(object):
  """Log class"""
  instance = None

  def __init__(self, configFile=None):
    if configFile:
      self.__config = Configuration(configFile, 'Logger')
      doLog = self.__config.get('log')
      self.logLvl = getattr(logging, self.__config.get('level').upper())
    else:
      doLog = True
      self.logLvl = logging.INFO
    if doLog:
      # create logger
      if configFile:
        self.logFileSize = self.__config.get('size')
        self.nbrOfBackups = self.__config.get('backups')
        self.logToConsole = self.__config.get('logconsole')
        self.logfile = self.__config.get('logfile')
      else:
        self.logFileSize = 100000
        self.nbrOfBackups = 2
        self.logToConsole = True
        self.logfile = ''
      # create formatter
      stringFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      datefmt = '%m/%d/%Y %I:%M:%S %p'
      self.__formatter = logging.Formatter(fmt=stringFormat, datefmt=datefmt)
    Log.instance = self

  def setConsoleHandler(self, logger):
    """
    Sets the console handler with the parameters to the given logger
    """
    if self.logToConsole:
      consoleHandler = logging.StreamHandler()
      consoleHandler.setLevel(self.logLvl)
      consoleHandler.setFormatter(self.__formatter)
      logger.addHandler(consoleHandler)

  def setLogFile(self, logger):
    """
    Sets the file loggerwith the parameters to the given logger
    """
    if isNotNull(self.logfile):
      maxBytes = getattr(logger, "rot_maxBytes", self.logFileSize)
      backupCount = getattr(logger, "rot_backupCount", self.nbrOfBackups)
      fileRotater = RotatingFileHandler(self.logfile, 'a', maxBytes,
                                        backupCount)
      fileRotater.setLevel(self.logLvl)
      fileRotater.setFormatter(self.__formatter)
      logger.addHandler(fileRotater)

  @classmethod
  def getInstance(cls):
    """
    Returns the instance of the logger
    """
    if Log.instance is None:
      Log.instance = Log()
      Log.instance.getLogger('Log').error('No configuration loaded')
    return Log.instance

  @staticmethod
  def getLogger(className):
    """
    Returns the instance for of the logger for the given class

    :returns: Logger
    """
    if Log.instance is None:
      return Log.getInstance().getLogger(className)
    else:
      logger = logging.getLogger(className)
      logger.setLevel(Log.getInstance().logLvl)
      Log.getInstance().setConsoleHandler(logger)
      Log.getInstance().setLogFile(logger)
      return logger
