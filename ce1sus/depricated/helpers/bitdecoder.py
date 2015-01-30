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


class BitRight(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can set group via rest inserts
  """

  PRIVILEGED = 0
  VALIDATE = 1
  SET_GROUP = 2

  @property
  def privileged(self):
    return self._get_value(BitRight.PRIVILEGED)

  @privileged.setter
  def privileged(self, value):
    self._set_value(BitRight.PRIVILEGED, value)

  @property
  def validate(self):
    return self._get_value(BitRight.VALIDATE)

  @validate.setter
  def validate(self, value):
    self._set_value(BitRight.VALIDATE, value)

  @property
  def set_group(self):
    return self._get_value(BitRight.SET_GROUP)

  @set_group.setter
  def set_group(self, value):
    self._set_value(BitRight.SET_GROUP, value)


class BitValue(BitBase):

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

  @property
  def is_proposal(self):
    return self._get_value(BitValue.PROPOSAL)

  @is_proposal.setter
  def is_proposal(self, value):
    self._set_value(BitValue.PROPOSAL, value)

  @property
  def is_rest_instert(self):
    return self._get_value(BitValue.REST_INSERT)

  @is_rest_instert.setter
  def is_rest_instert(self, value):
    self._set_value(BitValue.REST_INSERT, value)

  @property
  def is_web_insert(self):
    return self._get_value(BitValue.WEB_INSERT)

  @is_web_insert.setter
  def is_web_insert(self, value):
    self._set_value(BitValue.WEB_INSERT, value)

  @property
  def is_validated_and_shared(self):
    return self.is_validated and self.is_shareable

  @property
  def is_validated(self):
    return self._get_value(BitValue.VALIDATED)

  @is_validated.setter
  def is_validated(self, value):
    self._set_value(BitValue.VALIDATED, value)

  @property
  def is_shareable(self):
    return self._get_value(BitValue.SHARABLE)

  @is_shareable.setter
  def is_shareable(self, value):
    self._set_value(BitValue.SHARABLE, value)
