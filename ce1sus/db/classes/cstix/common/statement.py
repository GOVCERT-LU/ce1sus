# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.coa.relations import _REL_COA_IMPACT_STATEMENT, _REL_COA_COST_STATEMENT, _REL_EFFICACY_STATEMENT
from ce1sus.db.classes.cstix.common.relations import _REL_STATEMENT_STRUCTUREDTEXT, _REL_STATEMENT_INFORMATIONSOURCE, _REL_STATEMENT_CONFIDENCE
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICATOR_STATEMENT, _REL_TESTMECHANISM_STATEMENT
# from ce1sus.db.classes.cstix.relations import _REL_MARKINGSTRUCTURE_STATEMENT
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Statement(Entity, Base):

  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())
  timestamp_precision = Column('timestamp_precision', UnicodeType(10), default=u'seconds')
  value = Column('value', UnicodeType(255), nullable=False)
  description = relationship('StructuredText', secondary=_REL_STATEMENT_STRUCTUREDTEXT, uselist=False)
  source = relationship('InformationSource', uselist=False, secondary=_REL_STATEMENT_INFORMATIONSOURCE)
  confidence = relationship('Confidence', uselist=False, secondary=_REL_STATEMENT_CONFIDENCE)

  _PARENTS = ['base_test_mechanism',
              'indicator',
              'coa_impact',
              'coa_cost',
              'coa_efficacy',
              'simple_marking_structure'
              ]

  coa_impact = relationship('CourseOfAction', secondary=_REL_COA_IMPACT_STATEMENT, uselist=False)
  coa_cost = relationship('CourseOfAction', secondary=_REL_COA_COST_STATEMENT, uselist=False)
  coa_efficacy = relationship('CourseOfAction', secondary=_REL_EFFICACY_STATEMENT, uselist=False)
  # simple_marking_structure = relationship('SimpleMarkingStructure', secondary=_REL_MARKINGSTRUCTURE_STATEMENT, uselist=False)
  base_test_mechanism = relationship('BaseTestMechanism', secondary=_REL_TESTMECHANISM_STATEMENT, uselist=False)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_STATEMENT)

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'value': self.convert_value(self.value),
                'description': self.attribute_to_dict(self.description, cache_object),
                'source': self.attribute_to_dict(self.source, cache_object),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
               }
    else:
      result = {
                'timestamp': self.convert_value(self.timestamp),
                'timestamp_precision': self.convert_value(self.timestamp_precision),
                'value': self.convert_value(self.value),
               }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
