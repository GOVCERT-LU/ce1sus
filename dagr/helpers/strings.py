# -*- coding: utf-8 -*-

"""
String helper module

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import re
import cgi
import dateutil.parser
import json


class InputException(Exception):
  """
  Base exception for input exceptions
  """
pass


def plaintext2html(text, tabstop=4, make_br=True):
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
      return cgi.escape(characters['htmlchars'])
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
    string_text = string_text.replace('\"', '&quot;')
  else:
    string_text = ''
  return string_text


def stringToDateTime(string):
  """
  Converts a string to a DateTime if the format is known
  """
  try:
    if string:
      return dateutil.parser.parse(string)
    return None
  except:
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
