"""String helper module"""
import re
import cgi
from datetime import datetime

def plaintext2html(text, tabstop=4):
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
      return '<br>'
    elif characters['space']:
      t = string.group().replace('\t', '&nbsp;' * tabstop)
      t = t.replace(' ', '&nbsp;')
      return t
    elif characters['space'] == '\t':
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
          last = '<br>'
        return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
  if text and len(text) > 0:
    return re.sub(re_string, replacements, text)
  else:
    return ''

def stringToDateTime(string):
  return datetime.strptime(string, "%d/%m/%Y - %H:%M")

def isNotNull(value):
  """
  Checks if a string is not null

  :returns: Boolean
  """
  return value is not None and len(value) > 0
