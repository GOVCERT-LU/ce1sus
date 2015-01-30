# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from ce1sus.db.common.session import BaseClass
from ce1sus.depricated.brokers.basefoo import BASE


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class OldCe1susConfig(BASE):
  """
  Container class for the ce1sus configuration
  """
  __tablename__ = 'ce1sus'
  identifier = Column('ce1sus_id', Integer, primary_key=True)
  key = Column('key', String)
  value = Column('value', String)

  def to_dict(self):
    return {'identifier': BaseClass.convert_value(self.identifier),
            'key': BaseClass.convert_value(self.key),
            'value': BaseClass.convert_value(self.value)
            }

  def validate(self):
    """
    Returns true if the object is valid
    """
    return self
