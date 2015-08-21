# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.identity import Identity
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
from ce1sus.db.classes.cstix.incident.relations import _REL_LEVERAGEDTTP_RELATED_TTP, _REL_INCIDENT_IDENTITY, _REL_INCIDENT_RELATED_THREATACTOR, \
  _REL_INCIDENT_RELATED_INDICATOR, _REL_INCIDENT_RELATED_OBSERVABLE, _REL_INCIDENT_RELATED_INCIDENT, _REL_INCIDENT_RELATED_PACKAGES, \
  _REL_INCIDENT_INTENDED_EFFECT, _REL_INCIDENT_INFORMATIONSOURCE_REP, _REL_INCIDENT_INFORMATIONSOURCE_RES, _REL_INCIDENT_INFORMATIONSOURCE_COO, \
  _REL_INCIDENT_HANDLING, _REL_INCIDENT_CONFIDENCE, _REL_INCIDENT_COATAKEN, _REL_INCIDENT_COAREQUESTED
from ce1sus.db.classes.cstix.incident.time import Time
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LeveragedTTP(Entity, Base):
  scope = Column('scope', UnicodeType(255))
  leveraged_ttp = relationship(RelatedTTP, secondary=_REL_LEVERAGEDTTP_RELATED_TTP)
  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['incident']
  incident = relationship('Incident', uselist=False)

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
  incident = relationship('Incident', uselist=False)

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

  _PARENTS = ['incident']

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

  _PARENTS = ['incident']
  incident = relationship('Incident', uselist=False)

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

  time = relationship(Time, uselist=False)
  victims = relationship(Identity, secondary=_REL_INCIDENT_IDENTITY)
  attributed_threat_actors = relationship(RelatedThreatActor, secondary=_REL_INCIDENT_RELATED_THREATACTOR)
  related_indicators = relationship(RelatedIndicator, secondary=_REL_INCIDENT_RELATED_INDICATOR)
  related_observables = relationship(RelatedObservable, secondary=_REL_INCIDENT_RELATED_OBSERVABLE)
  related_incidents = relationship(RelatedIncident, secondary=_REL_INCIDENT_RELATED_INCIDENT)
  related_packages = relationship(RelatedPackageRef, secondary=_REL_INCIDENT_RELATED_PACKAGES)
  affected_assets = relationship(AffectedAsset)
  categories = relationship(IncidentCategory)
  intended_effects = relationship(IntendedEffect, secondary=_REL_INCIDENT_INTENDED_EFFECT)
  leveraged_ttps = relationship(LeveragedTTP, uselist=False)
  discovery_methods = relationship(DiscoveryMethod)
  reporter = relationship('InformationSource', uselist=False, secondary=_REL_INCIDENT_INFORMATIONSOURCE_REP)
  responders = relationship('InformationSource', secondary=_REL_INCIDENT_INFORMATIONSOURCE_RES)
  coordinators = relationship('InformationSource', secondary=_REL_INCIDENT_INFORMATIONSOURCE_COO)
  external_ids = relationship(ExternalID)
  impact_assessment = relationship(ImpactAssessment, uselist=False)
  security_compromise_id = Column('security_compromise_id', Integer)
  handling = relationship(MarkingSpecification, secondary=_REL_INCIDENT_HANDLING)
  __security_compromise = None

  _PARENTS = ['event', 'related_incident']
  related_incident = relationship('RelatedIncident', uselist=False, primaryjoin='RelatedIncident.child_id==Incident.identifier')
  event = relationship('Event', uselist=False)

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

  confidence = relationship(Confidence, secondary=_REL_INCIDENT_CONFIDENCE, uselist=False)
  coa_taken = relationship(COATaken, secondary=_REL_INCIDENT_COATAKEN)
  coa_requested = relationship(COARequested, secondary=_REL_INCIDENT_COAREQUESTED)
  history = relationship(HistoryItem)


  # ce1sus specific
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

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
