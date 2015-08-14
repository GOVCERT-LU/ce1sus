# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.indicator.test_mechanism import BaseTestMechanism, _REL_TESTMECHANISM_STRUCTUREDTEXT, _REL_TESTMECHANISM_VOCABSTRING
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeTextType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GenericTestMechanism(BaseTestMechanism):

  # override identifier to keep the polymorphics
  identifier = Column(BigIntegerType, ForeignKey('basetestmechanisms.basetestmechanism_id'), primary_key=True)
  # TODO: reference_location
  description = relationship(StructuredText, secondary=_REL_TESTMECHANISM_STRUCTUREDTEXT, uselist=False, backref='generic_test_meachanism_description')
  type_ = relationship(VocabString, secondary=_REL_TESTMECHANISM_VOCABSTRING, backref='generic_test_meachanism')
  specification = Column('specification', UnicodeTextType())

  __mapper_args__ = {'polymorphic_identity':'generictestmechanism'}

  def to_dict(self, cache_object):

    result = {
              'description': self.attribute_to_dict(self.description, cache_object),
              'type_': self.attribute_to_dict(self.type_, cache_object),
              'specification': self.convert_value(self.specification)
              }

    parent_dict = BaseTestMechanism.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
