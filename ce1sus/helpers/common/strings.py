# -*- coding: utf-8 -*-

"""
String helper module

Created: Jul, 2013
"""
import cgi
from datetime import datetime
import dateutil.parser
import re


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class InputException(Exception):
  """
  Base exception for input exceptions
  """


def plaintext2html(text, tabstop=4, make_br=True, mask=False):
  """
  returns the given text in HTML Code

  :param text: Text to be converted
  :type text: String
  :param tabstop: The number of indentations
  :type tabstop: Integer


  :returns: String
  """
  # reference http://djangosnippets.org/snippets/19/
  re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \\t]+)|' +
                         '(?P<lineend>\\r\\n|\\r|\\n)|(?P<protocal>(^|\\s)' +
                         '((http|ftp)://.*?))(\\s|$)', re.S | re.M | re.I)

  def replacements(string):
    """
    replacements

    :returns: String
    """
    characters = string.groupdict()
    if characters['htmlchars']:
      return cgi.escape(characters['htmlchars']).encode('utf-8', 'xmlcharrefreplace')
    if characters['lineend']:
      if make_br:
        return '<br/>'
      else:
        return characters['lineend']
    elif characters['space']:
      tabs = string.group().replace('\tabs', '&nbsp;' * tabstop)
      tabs = tabs.replace(' ', '&nbsp;')
      return tabs
    elif characters['space'] == '\tabs':
      return ' ' * tabstop
    else:
      url = string.group('protocal')
      if url.startswith(' '):
        prefix = ' '
        url = url[1:]
      else:
        prefix = ''
        last = string.groups()[-1]
        if last in ['\n', '\r', '\r\n']:
          if make_br:
            last = '<br/>'
        # I dont want links!
        # return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
        return '%s%s%s' % (prefix, url, last)

  # convert to text to be compliant
  string_text = u'{0}'.format(text)

  if len(string_text) > 0:
    string_text = re.sub(re_string, replacements, string_text)
    if mask:
      string_text = re.escape(string_text)
    else:
      string_text = string_text.replace('\"', '&quot;')
      string_text = string_text.replace('\'', '&#39;')
  else:
    string_text = ''
  # remove quotes

  return string_text


def stringToDateTime(string):
  """
  Converts a string to a DateTime if the format is known
  """
  try:
    if string:
      is_int = False
      if isinstance(string,int):
        is_int = True
      elif string.isdigit():
        is_int = True
      if is_int:
        try:
          return datetime.fromtimestamp(int(string) / 1000.0).replace(tzinfo=None)
        except ValueError:
          return None
      else:
        return dateutil.parser.parse(string).replace(tzinfo=None)
    return None
  except ValueError:
    raise InputException(u'Format of Date "{0}" is unknown'.format(string))


def cleanPostValue(value):
  result = None
  if isinstance(value, list):
    result = value[0]
  else:
    result = value
  if result:
    result.strip().encode('UTF-8', 'ignore')
  return result


def isNotNull(value):
  """
  Checks if a string is not null

  :returns: Boolean
  """
  if value is None:
    return False
  string = unicode(value)
  return string and string != ''
