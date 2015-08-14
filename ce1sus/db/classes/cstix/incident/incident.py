# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.intended_effect import IntendedEffect
from ce1sus.db.classes.cstix.common.related import RelatedThreatActor, RelatedIndicator, RelatedPackageRef, RelatedTTP, RelatedObservable, RelatedIncident
from ce1sus.db.classes.cstix.common.vocabs import DiscoveryMethod as VocabDiscoveryMethod
from ce1sus.db.classes.cstix.common.vocabs import IncidentCategory as VocabIncidentCategory
from ce1sus.db.classes.cstix.common.vocabs import IncidentStatus
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.cstix.incident.affected_asset import AffectedAsset
from ce1sus.db.classes.cstix.incident.coa import COATaken, COARequested
from ce1sus.db.classes.cstix.incident.external_id import ExternalID
from ce1sus.db.classes.cstix.incident.history import HistoryItem
from ce1sus.db.classes.cstix.incident.impact_assessment import ImpactAssessment
from ce1sus.db.classes.cstix.incident.time import Time
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_INCIDENT_HANDLING = Table('rel_incident_handling', getattr(Base, 'metadata'),
                                    Column('rih_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                    Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                    )

_REL_INCIDENT_IDENTITY = Table('rel_incident_identity', getattr(Base, 'metadata'),
                               Column('rii_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                               Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                               Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                               )

_REL_INCIDENT_RELATED_THREATACTOR = Table('rel_incident_rel_threatactor', getattr(Base, 'metadata'),
                                          Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                          Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                          Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                          )

_REL_INCIDENT_RELATED_INDICATOR = Table('rel_incident_rel_indicator', getattr(Base, 'metadata'),
                                        Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                        Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_INCIDENT_RELATED_OBSERVABLE = Table('rel_incident_rel_observable', getattr(Base, 'metadata'),
                                         Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                         Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                         Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                         )

_REL_INCIDENT_RELATED_INCIDENT = Table('rel_incident_rel_incident', getattr(Base, 'metadata'),
                                       Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                       Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )

_REL_INCIDENT_RELATED_PACKAGES = Table('rel_incident_relpackage_ref', getattr(Base, 'metadata'),
                                       Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                       Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )

_REL_LEVERAGEDTTP_RELATED_TTP = Table('rel_leveragedttp_rel_ttp', getattr(Base, 'metadata'),
                                      Column('rct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('leveragedttp_id', BigIntegerType, ForeignKey('leveragedttps.leveragedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                      Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                      )

_REL_INCIDENT_INFORMATIONSOURCE_REP = Table('rel_incident_informationsource_rep', getattr(Base, 'metadata'),
                                            Column('rii_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('incident_id',
                                                   BigIntegerType,
                                                   ForeignKey('incidents.incident_id',
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

_REL_INCIDENT_INFORMATIONSOURCE_RES = Table('rel_incident_informationsource_res', getattr(Base, 'metadata'),
                                            Column('rii_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('incident_id',
                                                   BigIntegerType,
                                                   ForeignKey('incidents.incident_id',
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

_REL_INCIDENT_INFORMATIONSOURCE_COO = Table('rel_incident_informationsource_coo', getattr(Base, 'metadata'),
                                            Column('rii_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('incident_id',
                                                   BigIntegerType,
                                                   ForeignKey('incidents.incident_id',
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
_REL_INCIDENT_COATAKEN = Table('rel_incident_coataken', getattr(Base, 'metadata'),
                                            Column('rict_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('incident_id',
                                                   BigIntegerType,
                                                   ForeignKey('incidents.incident_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   index=True,
                                                   nullable=False),
                                            Column('coataken_id',
                                                   BigIntegerType,
                                                   ForeignKey('coatakens.coataken_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   nullable=False,
                                                   index=True)
                                            )
_REL_INCIDENT_COAREQUESTED = Table('rel_incident_coarequested', getattr(Base, 'metadata'),
                                            Column('ricr_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('incident_id',
                                                   BigIntegerType,
                                                   ForeignKey('incidents.incident_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   index=True,
                                                   nullable=False),
                                            Column('coarequested_id',
                                                   BigIntegerType,
                                                   ForeignKey('coarequesteds.coarequested_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   nullable=False,
                                                   index=True)
                                            )

_REL_INCIDENT_STRUCTUREDTEXT = Table('rel_incident_structuredtext', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('incident_id',
                                              BigIntegerType,
                                              ForeignKey('incidents.incident_id',
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


_REL_INCIDENT_STRUCTUREDTEXT_SHORT = Table('rel_incident_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('incident_id',
                                              BigIntegerType,
                                              ForeignKey('incidents.incident_id',
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

_REL_INCIDENT_CONFIDENCE = Table('rel_incident_confidence', getattr(Base, 'metadata'),
                                              Column('rac_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('incident_id',
                                                     BigIntegerType,
                                                     ForeignKey('incidents.incident_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     index=True,
                                                     nullable=False),
                                              Column('confidence_id',
                                                     BigIntegerType,
                                                     ForeignKey('confidences.confidence_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     nullable=False,
                                                     index=True)
                                              )

_REL_INCIDENT_INTENDED_EFFECT = Table('rel_incident_intended_effect', getattr(Base, 'metadata'),
                                      Column('riie_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                      Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                      )


class LeveragedTTP(Entity, Base):
  scope = Column('scope', UnicodeType(255))
  leveraged_ttp = relationship(RelatedTTP, secondary=_REL_LEVERAGEDTTP_RELATED_TTP, backref='leveraged_ttp')
  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @property
  def parent(self):
    return self.incident

  def to_dict(self, cache_object):

    result = {
              'scope': self.convert_value(self.scope),
              'leveraged_ttp': self.attributelist_to_dict(self.leveraged_ttp, cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


class IncidentCategory(Entity, Base):
  category_id = Column('category_id', Integer, default=None, nullable=False)
  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  __value = None

  @property
  def value(self):
    if not self.__value:
      if self.status_id:
        self.__value = VocabIncidentCategory(self, 'category_id')
    return self.__value

  @value.setter
  def value(self, value):
    if not self.value:
      self.__value = VocabIncidentCategory(self, 'category_id')
    self.value.name = value

  @property
  def parent(self):
    return self.incident

  def to_dict(self, cache_object):

    result = {
              'value': self.convert_value(self.value)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class DiscoveryMethod(Entity, Base):
  discovery_id = Column('discovery_id', Integer, default=None, nullable=False)
  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  __value = None

  @property
  def parent(self):
    return self.incident

  @property
  def value(self):
    if not self.__value:
      if self.status_id:
        self.__value = VocabDiscoveryMethod(self, 'discovery_id')
    return self.__value

  @value.setter
  def value(self, value):
    if not self.value:
      self.__value = VocabDiscoveryMethod(self, 'discovery_id')
    self.value.name = value

  def to_dict(self, cache_object):

    result = {
              'value': self.convert_value(self.value)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class Incident(BaseCoreComponent, Base):

  status_id = Column('status_id', Integer)

  @property
  def status(self):
    if not self.__status:
      if self.status_id:
        self.__status = IncidentStatus(self, 'status_id')
    return self.__status

  @status.setter
  def status(self, value):
    if not self.status:
      self.__status = IncidentStatus(self, 'status_id')
    self.status.name = value

  time = relationship(Time, uselist=False, backref='incident')
  victims = relationship(Identity, secondary=_REL_INCIDENT_IDENTITY, backref='incident')
  attributed_threat_actors = relationship(RelatedThreatActor, secondary=_REL_INCIDENT_RELATED_THREATACTOR, backref='incident')
  related_indicators = relationship(RelatedIndicator, secondary=_REL_INCIDENT_RELATED_INDICATOR, backref='incident')
  related_observables = relationship(RelatedObservable, secondary=_REL_INCIDENT_RELATED_OBSERVABLE, backref='incident')
  related_incidents = relationship(RelatedIncident, secondary=_REL_INCIDENT_RELATED_INCIDENT, backref='incident')
  related_packages = relationship(RelatedPackageRef, secondary=_REL_INCIDENT_RELATED_PACKAGES, backref='incident')
  affected_assets = relationship(AffectedAsset, backref='incident')
  categories = relationship(IncidentCategory, backref='incident')
  intended_effects = relationship(IntendedEffect, secondary=_REL_INCIDENT_INTENDED_EFFECT, backref='incident')
  leveraged_ttps = relationship(LeveragedTTP, uselist=False, backref='incident')
  discovery_methods = relationship(DiscoveryMethod, backref='incident')
  reporter = relationship(InformationSource, uselist=False, secondary=_REL_INCIDENT_INFORMATIONSOURCE_REP, backref='incident_reporter')
  responders = relationship(InformationSource, secondary=_REL_INCIDENT_INFORMATIONSOURCE_RES, backref='incident_responder')
  coordinators = relationship(InformationSource, secondary=_REL_INCIDENT_INFORMATIONSOURCE_COO, backref='incident_coordinators')
  external_ids = relationship(ExternalID, backref='incident')
  impact_assessment = relationship(ImpactAssessment, uselist=False, backref='incident')
  security_compromise_id = Column('security_compromise_id', Integer)
  handling = relationship(MarkingSpecification, secondary=_REL_INCIDENT_HANDLING, backref='incident')
  __security_compromise = None

  @property
  def security_compromise(self):
    if not self.__security_compromise:
      if self.security_compromise_id:
        self.__security_compromise = IncidentStatus(self, 'security_compromise_id')
    return self.__security_compromise

  @security_compromise.setter
  def security_compromise(self, value):
    if not self.security_compromise:
      self.__security_compromise = IncidentStatus(self, 'security_compromise_id')
    self.security_compromise.name = value

  confidence = relationship(Confidence, secondary=_REL_INCIDENT_CONFIDENCE, uselist=False, backref='incident')
  coa_taken = relationship(COATaken, secondary=_REL_INCIDENT_COATAKEN, backref='incident')
  coa_requested = relationship(COARequested, secondary=_REL_INCIDENT_COAREQUESTED, backref='incident')
  history = relationship(HistoryItem, backref='incident')


  # ce1sus specific
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

  @property
  def parent(self):
    if self.event:
      return self.event
    elif self.related_incident:
      return self.related_incident
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'status': self.convert_value(self.status),
                'time': self.attribute_to_dict(self.time, cache_object),
                'victims': self.attributelist_to_dict(self.victims, cache_object),
                'attributed_threat_actors': self.attributelist_to_dict(self.attributed_threat_actors, cache_object),
                'related_indicators': self.attributelist_to_dict(self.related_indicators, cache_object),
                'related_observables': self.attributelist_to_dict(self.related_observables, cache_object),
                'related_incidents': self.attributelist_to_dict(self.related_incidents, cache_object),
                'affected_assets': self.attributelist_to_dict(self.affected_assets, cache_object),
                'categories': self.attributelist_to_dict(self.categories, cache_object),
                'intended_effects': self.attributelist_to_dict(self.intended_effects, cache_object),
                'leveraged_ttps': self.attribute_to_dict(self.leveraged_ttps, cache_object),
                'discovery_methods': self.attributelist_to_dict(self.discovery_methods, cache_object),
                'reporter': self.attribute_to_dict(self.reporter, cache_object),
                'responders': self.attributelist_to_dict(self.responders, cache_object),
                'coordinators': self.attributelist_to_dict(self.coordinators, cache_object),
                'external_ids': self.attributelist_to_dict(self.external_ids, cache_object),
                'impact_assessment': self.attribute_to_dict(self.impact_assessment, cache_object),
                'handling': self.attributelist_to_dict(self.handling, cache_object),
                'security_compromise': self.convert_value(self.security_compromise),
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'coa_taken': self.attributelist_to_dict(self.coa_taken, cache_object),
                'coa_requested': self.attributelist_to_dict(self.coa_requested, cache_object),
                'history': self.attributelist_to_dict(self.history, cache_object),
                }
    else:
      result = {
                'status': self.convert_value(self.status),
                'time': self.attribute_to_dict(self.time, cache_object),
                'victims': self.attributelist_to_dict(self.victims, cache_object),
                'reporter': self.attribute_to_dict(self.reporter, cache_object),
                }

    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
