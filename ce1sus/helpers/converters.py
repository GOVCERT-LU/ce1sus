from ce1sus.helpers.debug import Log
import ce1sus.helpers.string as string

def setString(instance, attribtue, value):
  try:
    setattr(instance, attribtue, unicode(value))
  except ValueError as e:
    setattr(instance, attribtue, None)
    Log.getLogger("converters").error(e)

def setInteger(instance, attribtue, value):
  try:
    setattr(instance, attribtue, int(value))
  except ValueError as e:
    setattr(instance, attribtue, None)
    Log.getLogger("converters").error(e)

def setDate(instance, attribtue, value):
  try:
    setattr(instance, attribtue, string.stringToDateTime(value))
  except ValueError as e:
    setattr(instance, attribtue, None)
    Log.getLogger("converters").error(e)
