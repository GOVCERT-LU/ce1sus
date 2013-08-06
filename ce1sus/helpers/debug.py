"""Debugging module"""

import os
import logging
from ce1sus.helpers.config import Configuration
from ce1sus.helpers.string import isNotNull
from logging.handlers import RotatingFileHandler




class Logger(object):
  """Logger class"""
  def __init__(self, configFile=None):

    if configFile:
      self.__config = Configuration(configFile, 'Logger')
      self.__doLog = self.__config.get('log')

      self.logLvl = getattr(logging, self.__config.get('level').upper())
    else:
      self.__doLog = True
      self.logLvl = logging.INFO


    if self.__doLog:
      # create logger

      self.__logger = logging.getLogger('root')

      if configFile:
        self.__logger.setLevel(self.logLvl)
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

      # create console Handler and set level to debug
      self.setConsoleHandler(self.__logger)


      self.setLogFile(self.__logger)

    Logger.instance = self

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


      # Remove the default FileHandlers if present.
      logger.error_file = ""
      logger.access_file = ""

      maxBytes = getattr(logger, "rot_maxBytes", self.logFileSize)
      backupCount = getattr(logger, "rot_backupCount", self.nbrOfBackups)

      fileRotater = RotatingFileHandler(self.logfile, 'a', maxBytes,
                                        backupCount)
      fileRotater.setLevel(self.logLvl)
      fileRotater.setFormatter(self.__formatter)
      logger.addHandler(fileRotater)

  @staticmethod
  def getLogger(className):
    """
    Returns the instance for of the logger for the given class

    :returns: Logger
    """
    if hasattr(Logger, 'instance'):
      logger = logging.getLogger(className)
      logger.setLevel(Logger.instance.logLvl)
      Logger.instance.setConsoleHandler(logger)
      Logger.instance.setLogFile(logger)
      return logger
    else:
      Logger()
      Logger.instance.getLogger('root').error('No configuration loaded')
      return Logger.instance.getLogger(className)


