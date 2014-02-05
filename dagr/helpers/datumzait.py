# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 13, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from datetime import datetime
import dateutil.tz


class DatumZait(datetime):
  """Wrapper for datetime"""

  @staticmethod
  def utcnow():
    """same as in datetime"""
    return datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

  @staticmethod
  def now():
    """same as in datetime"""
    return datetime.now()

  @staticmethod
  def strptime(date_string, date_format):
    """same as in datetime"""
    return datetime.strptime(date_string, date_format)
