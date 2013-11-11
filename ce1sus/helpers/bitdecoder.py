# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from types import IntType


class BitValue(object):

  """
  The __bitValue is defined as follows:
  [0] : Web insert
  [1] : Rest insert
  [2] : Is validated
  [3] : Is sharable
  """

  WEB_INSERT = 0
  REST_INSERT = 1
  VALIDATED = 2
  SHARABLE = 3

  def __init__(self, bitValue):
    if isinstance(bitValue, IntType):
      bits = bitValue
    else:
      bits = int('{0}'.format(bitValue), 2)
    self.__bitValue = bits

  @property
  def bitCode(self):
    return self.__bitValue

  @property
  def isRestInsert(self):
    return self.__getValue(BitValue.REST_INSERT)

  @isRestInsert.setter
  def isRestInsert(self, value):
    self.__setValue(BitValue.REST_INSERT, value)

  @property
  def isWebInsert(self):
    return self.__getValue(BitValue.WEB_INSERT)

  @isWebInsert.setter
  def isWebInsert(self, value):
    self.__setValue(BitValue.WEB_INSERT, value)

  @property
  def isValidated(self):
    return self.__getValue(BitValue.VALIDATED)

  @isValidated.setter
  def isValidated(self, value):
    self.__setValue(BitValue.VALIDATED, value)

  @property
  def isSharable(self):
    return self.__getValue(BitValue.SHARABLE)

  @isSharable.setter
  def isSharable(self, value):
    self.__setValue(BitValue.SHARABLE, value)

  def __getBit(self, offset):
    mask = 1 << offset
    return self.__bitValue & mask

  def __setBit(self, offset, value):
    mask = 1 << offset
    self.__bitValue = self.__bitVale | mask

  def __unsetBit(self, offset, value):
    mask = ~(1 << offset)
    self.__bitValue = self.__bitVale & mask

  def __setValue(self, offset, value):
    if value:
      self.__setBit(offset)
    else:
      self.__unsetBit(offset)

  def __countBits(self, value):
    return bin(value).count('1')

  def __getValue(self, offset):
    value = self.__getBit(offset)
    length = self.__countBits(value)
    return length > 0
