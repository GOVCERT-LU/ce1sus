# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BigInteger, Unicode

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.common.session import Base
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

  TEXT_VALUE = 0
  STRING_VALUE = 1
  DATE_VALUE = 2
  NUMBER_VALUE = 3
  TIMESTAMP_VALUE = 4

  @classmethod
  def get_dictionary(cls):
    return {ValueTable.TEXT_VALUE: u'Text',
            ValueTable.STRING_VALUE: u'String',
            ValueTable.DATE_VALUE: u'Date',
            ValueTable.NUMBER_VALUE: u'Number',
            ValueTable.TIMESTAMP_VALUE: u'TimeStamp'
            }

  @property
  def classname(self):
    return u'{0}Value'.format(ValueTable.get_by_id(self.identifier))

  @property
  def attribute(self):
    return u'{0}_value'.format(ValueTable.get_by_id(self.identifier)).lower()

  @classmethod
  def get_all_table_names(cls):
    result = list()
    for value in cls.get_dictionary().itervalues():
      result.append(value)
    return result


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


class ServerType(StaticBase):
  """Static class defining the risk of an event"""
  @classmethod
  def get_dictionary(cls):
    return {0: u'MISP',
            1: u'Ce1sus'}


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
  def is_proposal(self):
    return self._get_value(Properties.PROPOSAL)

  @is_proposal.setter
  def is_proposal(self, value):
    self._set_value(Properties.PROPOSAL, value)

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


class Marking(ExtendedLogingInformations, Base):
  version = Column('version', Unicode(40), default=u'1.0.0', nullable=False)
  controlled_structure = Column('controlled_structure', Unicode(255))
  markings = relationship('MarkingStructure')


class MarkingStructure(ExtendedLogingInformations, Base):
  marking_id = Column('marking_id', BigInteger, ForeignKey('markings.marking_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  marking_model_name = Column('marking_model_name', Unicode(255))
  marking_model_ref = Column('marking_model_ref', Unicode(255))
