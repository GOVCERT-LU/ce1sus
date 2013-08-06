from ce1sus.helpers.debug import Logger
import ce1sus.helpers.string as string

def setInteger(instance, attribtue, value):
  try:
    setattr(instance, attribtue, int(value))
  except ValueError as e:
    setattr(instance, attribtue, None)
    Logger.getLogger("converters").error(e)

def setDate(instance, attribtue, value):
  try:
    setattr(instance, attribtue, string.stringToDateTime(value))
  except ValueError as e:
    setattr(instance, attribtue, None)
    Logger.getLogger("converters").error(e)
