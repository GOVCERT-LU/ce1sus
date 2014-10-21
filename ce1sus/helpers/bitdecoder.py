# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BitBase(object):

  def __init__(self, bit_value, parentObj=None, attr_name='dbcode'):
    # TODO make an intvalue and check if between 0 and 15
    value = int('{0}'.format(bit_value))
    if (value >= 0) and (value <= 32):
      bits = value
    else:
      bits = int('{0}'.format(bit_value), 2)

    self.__parent_object = parentObj
    self.__bit_value = bits
    if hasattr(self.__parent_object, attr_name):
      setattr(self.__parent_object, attr_name, self.bit_code)

  @property
  def bit_code(self):
    return self.__bit_value

  def _get_bit(self, offset):
    mask = 1 << offset
    return self.__bit_value & mask

  def _set_bit(self, offset):
    mask = 1 << offset
    self.__bit_value = self.__bit_value | mask

  def _unset_bit(self, offset):
    mask = ~(1 << offset)
    self.__bit_value = self.__bit_value & mask

  def _set_value(self, offset, value):
    if value:
      self._set_bit(offset)
    else:
      self._unset_bit(offset)
    if self.__parent_object is not None:
      # check if parent has the correct attribute
      if hasattr(self.__parent_object, 'dbcode'):
        self.__parent_object.dbcode = self.bit_code

  def _count_set_bits(self, value):
    return bin(value).count('1')

  def _get_value(self, offset):
    value = self._get_bit(offset)
    length = self._count_set_bits(value)
    return length > 0
