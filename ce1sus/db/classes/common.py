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


class ValueException(Exception):
  pass


class StaticBase(object):

  def __init__(self, identifier):
    self.identifier = identifier

  @classmethod
  def get_dictionary(cls):
    raise StaticMappingException(u'Dictionary is not defined for class {0}', cls.__name___)

  @classmethod
  def get_by_id(cls, identifier):
    if hasattr(identifier, 'error'):
      return identifier
    else:
      identifier = int(identifier)
      if identifier in cls.get_dictionary().keys():
        value = cls.get_dictionary().get(identifier, None)
      if value:
        return value
      else:
        raise StaticMappingException(u'Invalid input "{0}" for class {1}'.format(identifier, cls.__name___))

  @classmethod
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

  @classmethod
  def get_all(cls):
    return cls.get_dictionary()

  @classmethod
  def get_all_inverted(cls):
    return StaticBase.invert_dict(cls.get_dictionary())

  @property
  def value(self):
    """Gets the name of the TLP level"""
    return self.get_by_id(self.identifier)

  @classmethod
  def get_cb_values(cls):
    result = list()
    for key, value in cls.get_dictionary().iteritems():
      result.append({'identifier': key, 'name': value})
    return result


class ValueTable(StaticBase):

  @classmethod
  def get_dictionary(cls):
    return {0: u'Text',
            1: u'String',
            2: u'Date',
            3: u'Number',
            4: u'TimeStamp',
            5: u'Date'}

  @property
  def classname(self):
    return u'{0}Value'.format(ValueTable.get_by_id(self.identifier))

  @property
  def attribute(self):
    return u'{0}_value'.format(ValueTable.get_by_id(self.identifier)).lower()


class Analysis(StaticBase):
  """Static class defining the status the analysis of an event"""

  @classmethod
  def get_dictionary(cls):
    return {0: u'None',
            1: u'Opened',
            2: u'Stalled',
            3: u'Completed',
            4: u'Unknown'}


class Confidence(StaticBase):

  @classmethod
  def get_dictionary(cls):
    return {0: u'None',
            1: u'Low',
            2: u'Medium',
            3: u'High'}


class Risk(StaticBase):
  """Static class defining the risk of an event"""
  @classmethod
  def get_dictionary(cls):
    return {0: u'None',
            1: u'Low',
            2: u'Medium',
            3: u'High',
            4: u'Undefined'}


class Status(StaticBase):
  """Static class defining the status of an event"""
  @classmethod
  def get_dictionary(cls):
    return {0: u'Confirmed',
            1: u'Draft',
            2: u'Deleted',
            3: u'Expired'}


class TLP(StaticBase):

  @classmethod
  def get_dictionary(cls):
    return {0: u'Red',
            1: u'Amber',
            2: u'Green',
            3: u'White'
            }


class Properties(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : Is validated
  [1] : Is sharable - On event lvl it has the same meaning as published
  [2] : Is proposal
  """
  # 4
  VALIDATED = 0
  # 8
  SHARABLE = 1
  # 16
  PROPOSAL = 2

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

  def to_dict(self):
    return {'validated': self.is_validated,
            'shared': self.is_shareable,
            'proposal': self.is_proposal
            }

  def populate(self, json):
    if json:
      validated = json.get('validated', False)
      self.is_validated = validated

      share = json.get('shared', False)
      self.is_shareable = share
      # Note proposal is handled internally only by the engine
