# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.indicator.relations import _REL_TESTMECHANISM_VOCABSTRING
from ce1sus.db.classes.internal.corebase import UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'




class VocabString(Entity, Base):

  value = Column('value', UnicodeType(255), index=True, nullable=False)
  xsi_type = Column('xsi_type', UnicodeType(255), index=True, nullable=False)
  vocab_name = Column('vocab_name', UnicodeType(255), index=True, nullable=False)
  vocab_reference = Column('vocab_reference', UnicodeTextType())

  _PARENTS = ['generic_test_meachanism']
  generic_test_meachanism = relationship('GenericTestMechanism', uselist=False, secondary=_REL_TESTMECHANISM_VOCABSTRING)

  def to_dict(self, cache_object):

    result = {'value': self.convert_value(self.value),
              'xsi_type': self.convert_value(self.xsi_type),
              'vocab_name': self.convert_value(self.vocab_name),
              'vocab_reference': self.convert_value(self.vocab_reference),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)