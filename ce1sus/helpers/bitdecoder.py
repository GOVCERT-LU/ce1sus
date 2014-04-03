# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BitValue(object):

  """
  The __bit_value is defined as follows:
  [0] : Web insert
  [1] : Rest insert
  [2] : Is validated
  [3] : Is sharable
  """

  # 1
  WEB_INSERT = 0
  # 2
  REST_INSERT = 1
  # 4
  VALIDATED = 2
  # 8
  SHARABLE = 3
  # 16
  PROPOSAL = 4

  def __init__(self, bit_value, parentObj=None):
    # TODO make an intvalue and check if between 0 and 15
    value = int('{0}'.format(bit_value))
    if (value >= 0) and (value <= 32):
      bits = value
    else:
      bits = int('{0}'.format(bit_value), 2)

    self.__parent_object = parentObj
    self.__bit_value = bits
    if hasattr(self.__parent_object, 'dbcode'):
        self.__parent_object.dbcode = self.bit_code

  @property
  def bit_code(self):
    return self.__bit_value

  @property
  def is_proposal(self):
    return self.__get_value(BitValue.PROPOSAL)

  @is_proposal.setter
  def is_proposal(self, value):
    self.__set_value(BitValue.PROPOSAL, value)

  @property
  def is_rest_instert(self):
    return self.__get_value(BitValue.REST_INSERT)

  @is_rest_instert.setter
  def is_rest_instert(self, value):
    self.__set_value(BitValue.REST_INSERT, value)

  @property
  def is_web_insert(self):
    return self.__get_value(BitValue.WEB_INSERT)

  @is_web_insert.setter
  def is_web_insert(self, value):
    self.__set_value(BitValue.WEB_INSERT, value)

  @property
  def is_validated_and_shared(self):
    return self.is_validated and self.is_shareable

  @property
  def is_validated(self):
    return self.__get_value(BitValue.VALIDATED)

  @is_validated.setter
  def is_validated(self, value):
    self.__set_value(BitValue.VALIDATED, value)

  @property
  def is_shareable(self):
    return self.__get_value(BitValue.SHARABLE)

  @is_shareable.setter
  def is_shareable(self, value):
    self.__set_value(BitValue.SHARABLE, value)

  def __get_bit(self, offset):
    mask = 1 << offset
    return self.__bit_value & mask

  def __set_bit(self, offset):
    mask = 1 << offset
    self.__bit_value = self.__bit_value | mask

  def __unset_bit(self, offset):
    mask = ~(1 << offset)
    self.__bit_value = self.__bit_value & mask

  def __set_value(self, offset, value):
    if value:
      self.__set_bit(offset)
    else:
      self.__unset_bit(offset)
    if not self.__parent_object is None:
      # check if parent has the correct attribute
      if hasattr(self.__parent_object, 'dbcode'):
        self.__parent_object.dbcode = self.bit_code

  def __count_set_bits(self, value):
    return bin(value).count('1')

  def __get_value(self, offset):
    value = self.__get_bit(offset)
    length = self.__count_set_bits(value)
    return length > 0
