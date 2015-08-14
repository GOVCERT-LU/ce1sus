# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhaseReference
from ce1sus.db.classes.cstix.common.related import RelatedPackageRef, RelatedCampaign, RelatedIndicator, RelatedTTP
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.cstix.common.vocabs import IndicatorType as VocabIndicatorType
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.cstix.indicator.test_mechanism import BaseTestMechanism
from ce1sus.db.classes.cstix.indicator.valid_time import ValidTime
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_INDICATOR_KILLCHAINPHASEREF = Table('rel_indicator_killchainphase_ref', getattr(Base, 'metadata'),
                                      Column('rik_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                      Column('killchainphasereference_id', BigIntegerType, ForeignKey('killchainphasereferences.killchainphasereference_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                      )

_REL_INDICATOR_OBSERVABLE = Table('rel_indicator_observable', getattr(Base, 'metadata'),
                                  Column('rio_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                  Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_INDICATOR_RELATED_TTPS = Table('rel_indicator_related_ttps', getattr(Base, 'metadata'),
                                    Column('rirt_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                    Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                    )

_REL_INDICATOR_RELATED_PACKAGES = Table('rel_indicator_relpackage_ref', getattr(Base, 'metadata'),
                                        Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                        Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_INDICATOR_RELATED_INDICATOR = Table('rel_indicator_related_indicators', getattr(Base, 'metadata'),
                                         Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                         Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                         Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                         )

_REL_INDICATOR_RELATED_CAMPAIGN = Table('rel_indicator_rel_indicator', getattr(Base, 'metadata'),
                                        Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_INDICATOR_HANDLING = Table('rel_indicator_handling', getattr(Base, 'metadata'),
                                        Column('rih_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_INDICATOR_CONFIDENCE = Table('rel_indicator_confidence', getattr(Base, 'metadata'),
                                        Column('ric_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_INDICATOR_STRUCTUREDTEXT = Table('rel_indicator_structuredtext', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('indicator_id',
                                              BigIntegerType,
                                              ForeignKey('indicators.indicator_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

_REL_INDICATOR_STRUCTUREDTEXT_SHORT = Table('rel_indicator_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('indicator_id',
                                              BigIntegerType,
                                              ForeignKey('indicators.indicator_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

_REL_INDICAOTR_INFORMATIONSOURCE = Table('rel_indicator_informationsource', getattr(Base, 'metadata'),
                                       Column('riis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('indicator_id',
                                              BigIntegerType,
                                              ForeignKey('indicators.indicator_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('informationsource_id',
                                             BigIntegerType,
                                             ForeignKey('informationsources.informationsource_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

_REL_INDICATOR_STATEMENT = Table('rel_indicator_statement', getattr(Base, 'metadata'),
                                       Column('ris_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('indicator_id',
                                              BigIntegerType,
                                              ForeignKey('indicators.indicator_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('statement_id',
                                             BigIntegerType,
                                             ForeignKey('statements.statement_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

class IndicatorType(Entity, Base):

  type_id = Column('type', Integer, default=None, nullable=False)
  indicator_id = Column(BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  __type_ = None

  @property
  def parent(self):
    return self.indicator

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

  def to_dict(self, cache_object):

    result = {
              'type_': self.convert_value(self.type_)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class Indicator(BaseCoreComponent, Base):

  producer = relationship(InformationSource, secondary=_REL_INDICAOTR_INFORMATIONSOURCE, uselist=False, backref='indicator')
  observables = relationship(Observable, secondary=_REL_INDICATOR_OBSERVABLE, backref='indicator')
  types = relationship(IndicatorType, backref='indicator')
  confidence = relationship(Confidence, secondary=_REL_INDICATOR_CONFIDENCE, uselist=False, backref='indicator')
  indicated_ttps = relationship(RelatedTTP, secondary=_REL_INDICATOR_RELATED_TTPS, backref='indicator')
  test_mechanisms = relationship(BaseTestMechanism, backref='indicator')
  alternative_id = Column('alternative_id', UnicodeType(255))
  # TODO: suggested_coas
  # suggested_coas = relationship('RelatedCOA', secondary='rel_indicator_related_coas')
  sightings = relationship(Sighting, backref='indicator')
  operator = Column('operator', UnicodeType(3))
  handling = relationship(MarkingSpecification, secondary=_REL_INDICATOR_HANDLING, backref='indicator')
  kill_chain_phases = relationship(KillChainPhaseReference, secondary=_REL_INDICATOR_KILLCHAINPHASEREF, backref='indicator')
  valid_time_positions = relationship(ValidTime, backref='indicator')
  related_indicators = relationship(RelatedIndicator, secondary=_REL_INDICATOR_RELATED_INDICATOR, backref='indicator')
  related_campaigns = relationship(RelatedCampaign, secondary=_REL_INDICATOR_RELATED_CAMPAIGN, backref='indicator')




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

  likely_impact = relationship(Statement, secondary=_REL_INDICATOR_STATEMENT, uselist=False, backref='indicator')
  negate = Column('negate', Boolean, default=None)
  related_packages = relationship(RelatedPackageRef, secondary=_REL_INDICATOR_RELATED_PACKAGES, backref='indicator')

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @property
  def parent(self):
    if self.event:
      return self.event
    elif self.related_indicator:
      return self.related_indicator
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):
    observables = self.attributelist_to_dict(self.observables, cache_object)
    observables_count = len(observables)
    if cache_object.complete:
      result = {'observables': observables,
                'observables_count': observables_count,
                'types': self.attributelist_to_dict(self.types, cache_object),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'indicated_ttps': self.attributelist_to_dict(self.indicated_ttps, cache_object),
                'alternative_id': self.convert_value(self.alternative_id),
                'sightings': self.attributelist_to_dict(self.sightings, cache_object),
                'killchains': self.attributelist_to_dict(self.killchains, cache_object),
                'valid_time_positions': self.attributelist_to_dict(self.valid_time_positions, cache_object),
                'related_indicators': self.attributelist_to_dict(self.related_indicators, cache_object),
                'related_campaigns': self.attributelist_to_dict(self.related_campaigns, cache_object),
                'operator': self.convert_value(self.operator),
                'observable_composition_operator': self.convert_value(self.observable_composition_operator),
                'producer': self.attribute_to_dict(self.producer, cache_object),
                'likely_impact': self.attribute_to_dict(self.likely_impact, cache_object),
                'negate': self.convert_value(self.negate),
                'related_packages': self.attributelist_to_dict(self.related_packages, cache_object)
                }
    else:
      result = {'observables': observables,
                'observables_count': observables_count,
                'types': self.attributelist_to_dict(self.types, cache_object),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'valid_time_positions': self.attributelist_to_dict(self.valid_time_positions, cache_object),
                'operator': self.convert_value(self.operator),
                'observable_composition_operator': self.convert_value(self.observable_composition_operator),
                'producer': self.attribute_to_dict(self.producer, cache_object),
                'negate': self.convert_value(self.negate),
                }

    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
