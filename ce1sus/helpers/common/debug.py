# -*- coding: utf-8 -*-

"""
Debugging module

Created: Jul, 2013
"""
import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import exists, dirname


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class Log(object):
  """Log class"""

  def __init__(self, config=None):

    if config:
      self.__config_section = config.get_section('Logger')
      do_log = self.__config_section.get('log')
      self.log_lvl = getattr(logging, self.__config_section.get('level').upper())
      self.log_console = self.__config_section.get('logconsole')
      self.log_file = self.__config_section.get('log_file')
    else:
      self.__config_section = None
      do_log = True
      self.log_lvl = logging.INFO
      self.log_console = True
      self.log_file = ''

    if do_log:
      # create formatter
      log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      datefmt = '%m/%d/%Y %I:%M:%S %p'
      self.__formatter = logging.Formatter(log_format)

  def __set_console_handler(self, logger):
    """
    Sets the console handler with the parameters to the given logger
    """
    if self.log_console:
      logger.setLevel(self.log_lvl)
      console_handler = logging.StreamHandler()
      console_handler.setFormatter(self.__formatter)
      logger.addHandler(console_handler)
      logger.setLevel(self.log_lvl)
      logger.handler_set = True

  def __set_logfile(self, logger):
    """
    Sets the file loggerwith the parameters to the given logger
    """
    if self.__config_section:
      log_file_size = self.__config_section.get('size')
      nbr_backups = self.__config_section.get('backups')
    else:
      log_file_size = 100000
      nbr_backups = 2
    if self.log_file:
      logger.setLevel(self.log_lvl)
      max_bytes = getattr(logger, "rot_maxBytes", log_file_size)
      backup_count = getattr(logger, "rot_backupCount", nbr_backups)
      # TODO: create director
      if not exists(dirname(self.log_file)):
        makedirs(dirname(self.log_file))
      file_rotater = RotatingFileHandler(self.log_file, 'a', max_bytes,
                                         backup_count)
      file_rotater.setFormatter(self.__formatter)
      logger.addHandler(file_rotater)
      logger.setLevel(self.log_lvl)
      logger.handler_set = True

  def get_logger(self, classname):
    """
    Returns the instance for of the logger for the given class

    :returns: Logger
    """
    logger = logging.getLogger(classname)
    if not getattr(logger, 'handler_set', None):
      if self.__config_section:
        self.__set_logfile(logger)
      self.__set_console_handler(logger)
    return logger

  def is_logger_cached(self, classname):
    """
    Checks is the logger for the given class is cached
    """
    return not (self.loggers.get(classname, None) is None)
