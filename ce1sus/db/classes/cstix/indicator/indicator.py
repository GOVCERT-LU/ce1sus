# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhaseReference
from ce1sus.db.classes.cstix.common.vocabs import IndicatorType as VocabIndicatorType
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICAOTR_INFORMATIONSOURCE, _REL_INDICATOR_OBSERVABLE, _REL_INDICATOR_CONFIDENCE, \
  _REL_INDICATOR_RELATED_TTPS, _REL_INDICATOR_HANDLING, _REL_INDICATOR_KILLCHAINPHASEREF, _REL_INDICATOR_RELATED_INDICATOR, _REL_INDICATOR_RELATED_CAMPAIGN, \
  _REL_INDICATOR_STATEMENT, _REL_INDICATOR_RELATED_PACKAGES
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.cstix.indicator.test_mechanism import BaseTestMechanism
from ce1sus.db.classes.cstix.indicator.valid_time import ValidTime
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.classes.internal.relations import _REL_EVENT_INDICATOR
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class IndicatorType(Entity, Base):

  type_id = Column('type', Integer, default=None, nullable=False)
  indicator_id = Column(BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __type_ = None

  _PARENTS = ['indicator']
  indicator = relationship('Indicator', uselist=False)

  @property
  def type_(self):
    if not self.__type_:
      if self.type_id:
        self.__type_ = VocabIndicatorType(self, 'type_id')
    return self.__type_

  @type_.setter
  def type_(self, type_):
    if not self.type_:
      self.__type_ = VocabIndicatorType(self, 'type_id')
    self.type_.name = type_

  @property
  def value(self):
    return self.type_.name

  @value.setter
  def value(self, value):
    self.type_ = value

  def to_dict(self, cache_object):

    result = {
              'type_': self.convert_value(self.type_.name)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class Indicator(BaseCoreComponent, Base):

  producer = relationship('InformationSource', secondary=_REL_INDICAOTR_INFORMATIONSOURCE, uselist=False)
  observables = relationship('Observable', secondary=_REL_INDICATOR_OBSERVABLE, back_populates='indicator')
  types = relationship(IndicatorType)
  confidence = relationship(Confidence, secondary=_REL_INDICATOR_CONFIDENCE, uselist=False)
  indicated_ttps = relationship('RelatedTTP', secondary=_REL_INDICATOR_RELATED_TTPS)
  test_mechanisms = relationship(BaseTestMechanism)
  alternative_id = Column('alternative_id', UnicodeType(255))
  # TODO: suggested_coas
  # suggested_coas = relationship('RelatedCOA', secondary='rel_indicator_related_coas')
  sightings = relationship(Sighting, back_populates='indicator')
  operator = Column('operator', UnicodeType(3))
  handling = relationship('MarkingSpecification', secondary=_REL_INDICATOR_HANDLING)
  kill_chain_phases = relationship(KillChainPhaseReference, secondary=_REL_INDICATOR_KILLCHAINPHASEREF)
  valid_time_positions = relationship(ValidTime)
  related_indicators = relationship('RelatedIndicator', secondary=_REL_INDICATOR_RELATED_INDICATOR)
  related_campaigns = relationship('RelatedCampaign', secondary=_REL_INDICATOR_RELATED_CAMPAIGN)


  _PARENTS = ['event', 'related_indicator']
  event = relationship('Event', secondary=_REL_EVENT_INDICATOR, uselist=False)
  related_indicator = relationship('RelatedIndicator', uselist=False, primaryjoin='RelatedIndicator.child_id==Indicator.identifier')

  @property
  def composite_indicator_expression(self):
    return self.operator

  @composite_indicator_expression.setter
  def composite_indicator_expression(self, operator):
    self.operator = operator

  @property
  def indicator_types(self):
    return self.types

  @indicator_types.setter
  def indicator_types(self, indicator_types):
    self.types = indicator_types

  @property
  def observable_composition_operator(self):
    return self.operator

  @observable_composition_operator.setter
  def observable_composition_operator(self, value):
    self.operator = value

  likely_impact = relationship('Statement', secondary=_REL_INDICATOR_STATEMENT, uselist=False)
  negate = Column('negate', Boolean, default=None)
  related_packages = relationship('RelatedPackageRef', secondary=_REL_INDICATOR_RELATED_PACKAGES)

  def to_dict(self, cache_object):

    instance = self.get_instance([Indicator.producer, Indicator.confidence], cache_object)

    observables = instance.attributelist_to_dict('observables', cache_object)
    observables_count = len(observables)
    if cache_object.complete:
      result = {'observables': observables,
                'observables_count': observables_count,
                'types': instance.attributelist_to_dict('types', cache_object),
                'confidence': instance.attribute_to_dict(instance.confidence, cache_object),
                'indicated_ttps': instance.attributelist_to_dict('indicated_ttps', cache_object),
                'alternative_id': instance.convert_value(instance.alternative_id),
                'sightings': instance.attributelist_to_dict('sightings', cache_object),
                'killchains': instance.attributelist_to_dict('kill_chain_phases', cache_object),
                'valid_time_positions': instance.attributelist_to_dict('valid_time_positions', cache_object),
                'related_indicators': instance.attributelist_to_dict('related_indicators', cache_object),
                'related_campaigns': instance.attributelist_to_dict('related_campaigns', cache_object),
                'operator': instance.convert_value(instance.operator),
                'observable_composition_operator': instance.convert_value(instance.observable_composition_operator),
                'producer': instance.attribute_to_dict(instance.producer, cache_object),
                'likely_impact': instance.attribute_to_dict(instance.likely_impact, cache_object),
                'negate': instance.convert_value(instance.negate),
                'related_packages': instance.attributelist_to_dict('related_packages', cache_object)
                }
    else:
      result = {'observables': observables,
                'observables_count': observables_count,
                'types': instance.attributelist_to_dict('types', cache_object),
                'confidence': instance.attribute_to_dict(instance.confidence, cache_object),
                'valid_time_positions': instance.attributelist_to_dict('valid_time_positions', cache_object),
                'operator': instance.convert_value(instance.operator),
                'observable_composition_operator': instance.convert_value(instance.observable_composition_operator),
                'producer': instance.attribute_to_dict(instance.producer, cache_object),
                'negate': instance.convert_value(instance.negate),
                }

    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
