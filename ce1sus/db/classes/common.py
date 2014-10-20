# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from ce1sus.helpers.bitdecoder import BitBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StaticMappingException(Exception):
  pass


class StaticBase(object):

  def __init__(self, identifier):
    self.identifier = identifier

  @staticmethod
  def get_dictionary(cls):
    raise StaticMappingException(u'Dictionary is not defined for class {0}', cls.__name___)

  @staticmethod
  def get_by_id(cls, identifier):
    if hasattr(identifier, 'error'):
      return identifier
    else:
      identifier = int(identifier)
      if identifier in cls.get_dictionary().keys():
        value = cls.get_dictionary()[identifier]
      if value:
        return value
      else:
        raise StaticMappingException(u'Invalid input "{0}" for class {1}'.format(identifier, cls.__name___))

  @staticmethod
  def get_by_value(cls, value):
    """
    Returns they key of a dictionary by value if existing.

    return object
    """
    formatted_input = value.title()
    result = None
    for key, value in cls.get_dictionary().items():
      if formatted_input == value:
        result = key
        break
    if result is None:
      raise StaticMappingException(u'Invalid input "{0}"'.format(formatted_input))
    return result

  @staticmethod
  def invert_dict(dictionary):
    """
    Inverts Key value of a dictionary

    Returns: dictionary
    """
    result = dict()
    for key, value in dictionary.iteritems():
      result[value] = key
    return result

  @staticmethod
  def get_all(cls):
    return cls.get_dictionary()

  @staticmethod
  def get_all_inverted(cls):
    return StaticBase.invert_dict(cls.get_dictionary())

  @property
  def value(self):
    """Gets the name of the TLP level"""
    return self.get_by_id(self.identifier)

  @staticmethod
  def get_cb_values(cls):
    return cls.get_all_inverted()


class ValueTable(StaticBase):

  @staticmethod
  def get_dictionary(cls):
    return {0: u'Text',
            1: u'String',
            2: u'Date',
            3: u'Number',
            4: u'TimeStamp'}

  @property
  def classname(self):
    return u'{0}Value'.format(ValueTable.get_by_id(self.identifier))

  @property
  def attribute(self):
    return u'{0}_value'.format(ValueTable.get_by_id(self.identifier)).lower()


class Analysis(StaticBase):
  """Static class defining the status the analysis of an event"""
  @staticmethod
  def get_dictionary(cls):
    return {0: u'None',
            1: u'Opened',
            2: u'Stalled',
            3: u'Completed',
            4: u'Unknown'}


class Confidence(StaticBase):

  @staticmethod
  def get_dictionary(cls):
    return {0: u'None',
            1: u'Low',
            2: u'Medium',
            3: u'High'}


class Risk(StaticBase):
  """Static class defining the risk of an event"""
  @staticmethod
  def get_dictionary(cls):
    return {0: u'None',
            1: u'Low',
            2: u'Medium',
            3: u'High',
            4: u'Undefined'}


class Status(StaticBase):
  """Static class defining the status of an event"""
  @staticmethod
  def get_dictionary(cls):
    return {0: u'Confirmed',
            1: u'Draft',
            2: u'Deleted',
            3: u'Expired'}


class TLP(StaticBase):

  @staticmethod
  def get_dictionary(cls):
    return {0: (u'Red', u'#FF0000'),
            1: (u'Amber', u'#FFBF00'),
            2: (u'Green', u'#66B032'),
            3: (u'White', u'#FFFFFF')
            }

  @staticmethod
  def get_by_value(cls, value):
    formatted_input = value.title()
    result = None
    for key, value in cls.get_dictionary().items():
      if formatted_input == value[0]:
        result = key
        break
    if result is None:
      raise StaticMappingException(u'Invalid input "{0}"'.format(formatted_input))
    return result

  @staticmethod
  def get_cb_values(cls):
    result = dict()
    for key, value in cls.iteritems():
      result[value[0]] = key
    return result

  @property
  def color(self):
    """Gets the color of the TLP level"""
    return TLP.get_color_by_id(self.identifier)[1]

  @property
  def value(self):
    return TLP.get_color_by_id(self.identifier)[0]


class Properties(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : Web insert
  [1] : Rest insert
  [2] : Is validated
  [3] : Is sharable
  [4] : Is proposal
  [5] : Is published
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

  PUBLISHED = 5

  @property
  def is_proposal(self):
    return self._get_value(Properties.PROPOSAL)

  @is_proposal.setter
  def is_proposal(self, value):
    self._set_value(Properties.PROPOSAL, value)

  @property
  def is_rest_instert(self):
    return self._get_value(Properties.REST_INSERT)

  @is_rest_instert.setter
  def is_rest_instert(self, value):
    self._set_value(Properties.REST_INSERT, value)

  @property
  def is_web_insert(self):
    return self._get_value(Properties.WEB_INSERT)

  @is_web_insert.setter
  def is_web_insert(self, value):
    self._set_value(Properties.WEB_INSERT, value)

  @property
  def is_validated_and_shared(self):
    return self.is_validated and self.is_shareable

  @property
  def is_validated(self):
    return self._get_value(Properties.VALIDATED)

  @is_validated.setter
  def is_validated(self, value):
    self._set_value(Properties.VALIDATED, value)

  @property
  def is_shareable(self):
    return self._get_value(Properties.SHARABLE)

  @is_shareable.setter
  def is_shareable(self, value):
    self._set_value(Properties.SHARABLE, value)

  @property
  def is_published(self):
    return self._get_value(Properties.PUBLISHED)

  @is_published.setter
  def is_published(self, value):
    self._set_value(Properties.PUBLISHED, value)
