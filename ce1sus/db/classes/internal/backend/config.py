# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 20, 2014
"""
from sqlalchemy.schema import Column

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.core import SimpleLogingInformations
from ce1sus.db.classes.internal.corebase import BaseObject, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susConfig(BaseObject, Base):
  key = Column('key', UnicodeType(255), nullable=False, index=True)
  value = Column('value', UnicodeTextType(), nullable=False)

  def validate(self):
        # TODO: create validation for ce1susconfig
    """
    Returns true if the object is valid
    """
    return self

  def to_dict(self, cache_object):

    result = {
              'key': self.convert_value(self.key),
              'value': self.convert_value(self.value),
              }

    parent_dict = SimpleLogingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
