# -*- coding: utf-8 -*-

"""
module used for generating hashes

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import hashlib


def __genericHash(string, hashType, salt=''):
  """
  Returns hashed string
  """
  if not string or string is None:
    return ''
  function = getattr(hashlib, hashType)
  hasher = function()
  function = getattr(hasher, 'update')
  function(string + salt)
  return hasher.hexdigest()


def hashMD5(string, salt=''):
  """
  Returns an MD5 Hash string

  :param string:
  :type string:
  :param salt: Add a bit of salt to the hash?
  :type salt:

  :returns: String
  """
  return __genericHash(string, 'md5', salt)


def hashSHA1(string, salt=''):
  """
  Returns an SHA1 Hash string

  :param string:
  :type string:
  :param salt: Add a bit of salt to the hash?
  :type salt:

  :returns: String
  """
  return __genericHash(string, 'sha1', salt)


def hashSHA256(string, salt=''):
  """
  Returns an SHA256 Hash string

  :param string:
  :type string:
  :param salt: Add a bit of salt to the hash?
  :type salt:

  :returns: String
  """
  return __genericHash(string, 'sha256', salt)


def hashSHA384(string, salt=''):
  """
  Returns an SHA384 Hash string

  :param string:
  :type string:
  :param salt: Add a bit of salt to the hash?
  :type salt:

  :returns: String
  """
  return __genericHash(string, 'sha384', salt)


def hashSHA512(string, salt=''):
  """
  Returns an SHA512 Hash string

  :param string:
  :type string:
  :param salt: Add a bit of salt to the hash?
  :type salt:

  :returns: String
  """
  return __genericHash(string, 'sha512', salt)


def __genericFileHash(fileToHash, hashType, block_size=256 * 128):
  """
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
  """
  function = getattr(hashlib, hashType)
  hasher = function()
  function = getattr(hasher, 'update')
  with open(fileToHash, 'rb') as f:
    for chunk in iter(lambda: f.read(block_size), b''):
      function(chunk)
  return hasher.hexdigest()


def fileHashMD5(fileToHash, block_size=256 * 128):
  """
  Returns an MD5  Hash of a file

  :param fileToHash:
  :type fileToHash:
  :param block_size:
  :type block_size:

  :returns: String
  """
  return __genericFileHash(fileToHash, 'md5', block_size)


def fileHashSHA1(fileToHash, block_size=256 * 128):
  """
  Returns an SHA1 Hash of a file

  :param fileToHash:
  :type fileToHash:
  :param block_size:
  :type block_size:

  :returns: String
  """
  return __genericFileHash(fileToHash, 'sha1', block_size)


def fileHashSHA256(fileToHash, block_size=256 * 128):
  """
  Returns an SHA256  Hash of a file

  :param fileToHash:
  :type fileToHash:
  :param block_size:
  :type block_size:

  :returns: String
  """
  return __genericFileHash(fileToHash, 'sha256', block_size)


def fileHashSHA384(fileToHash, block_size=256 * 128):
  """
  Returns an SHA384  Hash of a file

  :param fileToHash:
  :type fileToHash:
  :param block_size:
  :type block_size:

  :returns: String
  """
  return __genericFileHash(fileToHash, 'sha384', block_size)


def fileHashSHA512(fileToHash, block_size=256 * 128):
  """
  Returns an SHA512  Hash of a file

  :param fileToHash:
  :type fileToHash:
  :param block_size:
  :type block_size:

  :returns: String
  """
  return __genericFileHash(fileToHash, 'sha512', block_size)
