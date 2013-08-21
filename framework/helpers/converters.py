
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.helpers.debug import Log
import framework.helpers.string as string


class ObjectConverter(object):

  @staticmethod
  def setString(instance, attribtue, value):
    try:
      setattr(instance, attribtue, unicode(value, 'utf-8', errors='replace'))
    except ValueError as e:
      setattr(instance, attribtue, None)
      Log.getLogger("ObjectConverter").error(e)

  @staticmethod
  def setInteger(instance, attribtue, value):
    try:
      setattr(instance, attribtue, int(value))
    except ValueError as e:
      setattr(instance, attribtue, None)
      Log.getLogger("ObjectConverter").error(e)

  @staticmethod
  def setDate(instance, attribtue, value):
    try:
      setattr(instance, attribtue, string.stringToDateTime(value))
    except ValueError as e:
      setattr(instance, attribtue, None)
      Log.getLogger("ObjectConverter").error(e)


class ValueConverter(object):

  @staticmethod
  def setString(value):
    try:
      return unicode(value, 'utf-8', errors='replace')
    except ValueError as e:
      return None
      Log.getLogger("ValueConverter").error(e)

  @staticmethod
  def setInteger(value):
    try:
      return int(value)
    except ValueError as e:
      return None
      Log.getLogger("ValueConverter").error(e)

  @staticmethod
  def setDate(value):
    try:
      return string.stringToDateTime(value)
    except ValueError as e:
      return None
      Log.getLogger("ValueConverter").error(e)
