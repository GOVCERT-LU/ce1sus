import re
import cgi

def plaintext2html(text, tabstop=4):
  #reference http://djangosnippets.org/snippets/19/
  re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)
  
  def do_sub(m):
    c = m.groupdict()
    if c['htmlchars']:
      return cgi.escape(c['htmlchars'])
    if c['lineend']:
      return '<br>'
    elif c['space']:
      t = m.group().replace('\t', '&nbsp;'*tabstop)
      t = t.replace(' ', '&nbsp;')
      return t
    elif c['space'] == '\t':
      return ' '*tabstop;
    else:
      url = m.group('protocal')
      if url.startswith(' '):
        prefix = ' '
        url = url[1:]
      else:
        prefix = ''
        last = m.groups()[-1]
        if last in ['\n', '\r', '\r\n']:
          last = '<br>'
        return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
  return re.sub(re_string, do_sub, text)

def IsNotNull(value):
    return value is not None and len(value) > 0