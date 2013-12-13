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

class datumzait(datetime):

  @staticmethod
  def utcnow():
    return datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

  @staticmethod
  def now():
    return datetime.now()

  @staticmethod
  def strptime(dateString, dateFormat):
    return datetime.strptime(dateString, dateFormat)
