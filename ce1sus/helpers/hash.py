'''
Created on Aug 7, 2013

@author: jhemp
'''
import hashlib

def hashSHA1(string, salt=''):
  """
  Returns hashed string
  """
  if not string or string is None:
    return ''
  if string == 'EXTERNALAUTH':
    return string
  hashedText = hashlib.sha1()
  function = getattr(hashedText, 'update')
  function(string + salt)
  return hashedText.hexdigest()
