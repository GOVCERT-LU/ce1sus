# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from datetime import datetime
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.relations import _REL_CAMPAIGN_RELATED_TTP, _REL_CAMPAIGN_RELATED_INDICATOR, _REL_CAMPAIGN_RELATED_THREATACTOR, \
  _REL_CAMPAIGN_RELATED_CAMPAIGN, _REL_CAMPAIGN_RELATED_PACKAGES
from ce1sus.db.classes.cstix.coa.relations import _REL_COA_RELCOA, _REL_COA_RELATED_PACKAGESREF
from ce1sus.db.classes.cstix.common.relations import _REL_IDENTITY_RELATED_IDENTITY
from ce1sus.db.classes.cstix.exploit_target.relations import _REL_EXPLOITTARGET_RELATED_EXPLOITTARGET, _REL_EXPLOITTARGET_RELATED_PACKAGES
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.cstix.incident.relations import _REL_INCIDENT_RELATED_THREATACTOR, _REL_INCIDENT_RELATED_INDICATOR, _REL_INCIDENT_RELATED_OBSERVABLE, \
  _REL_INCIDENT_RELATED_INCIDENT, _REL_INCIDENT_RELATED_PACKAGES, _REL_LEVERAGEDTTP_RELATED_TTP
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICATOR_RELATED_TTPS, _REL_INDICATOR_RELATED_INDICATOR, _REL_INDICATOR_RELATED_CAMPAIGN, \
  _REL_INDICATOR_RELATED_PACKAGES, _REL_SIGHTING_REL_OBSERVABLE
from ce1sus.db.classes.cstix.threat_actor.relations import _REL_THREATACTOR_RELATED_THREATACTOR, _REL_THREATACTOR_RELATED_PACKAGES
from ce1sus.db.classes.cstix.ttp.relations import _REL_TTP_RELATED_TTP, _REL_TTP_RELATED_EXPLOITTARGET, _REL_TTP_RELATED_PACKAGES
from ce1sus.db.classes.internal.relations import _REL_EVENT_RELATED_PACKAGES


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class BaseRelated(Entity):

  @declared_attr
  def confidence(self):
    return relationship('Confidence', secondary='rel_{0}_confidence'.format(self.get_classname().lower()), uselist=False)

  relationship = Column('relationship', UnicodeType(255))

  @declared_attr
  def information_source(self):
    return relationship('InformationSource', secondary='rel_{0}_infromationsource'.format(self.get_classname().lower()), uselist=False)

  @property
  def item(self):
    return self.child

  @item.setter
  def item(self, value):
    self.child = value

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'relationship':self.convert_value(self.relationship),
                'information_source': self.attribute_to_dict(self.information_source, cache_object),
                '{0}'.format(self.item.get_classname()): self.attribute_to_dict(self.item, cache_object)
               }
    else:
      result = {
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'relationship':self.convert_value(self.relationship),
                '{0}'.format(self.item.get_classname()): self.attribute_to_dict(self.item, cache_object)
               }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
  

class RelatedObservable(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Observable', primaryjoin='RelatedObservable.child_id==Observable.identifier', uselist=False)
  sighting = relationship('Sighting', uselist=False, secondary=_REL_SIGHTING_REL_OBSERVABLE)

  _PARENTS = ['sigthing', 'incident']
  incident = relationship('Incident', secondary=_REL_INCIDENT_RELATED_OBSERVABLE, uselist=False)

  def validate(self):
    # TODO: validate
    return True


class RelatedExploitTarget(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('exploittargets.exploittarget_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('ExploitTarget', uselist=False, primaryjoin='RelatedExploitTarget.child_id==ExploitTarget.identifier')

  exploit_target = relationship('ExploitTarget', uselist=False, secondary=_REL_EXPLOITTARGET_RELATED_EXPLOITTARGET)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_RELATED_EXPLOITTARGET)

  _PARENTS = ['victim_targeting', 'ttp', 'exploit_target']

class RelatedPackageRef(BaseRelated, Base):
  idref = Column('idref', UnicodeType(255), nullable=False)
  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_RELATED_PACKAGES, uselist=False)
  coa = relationship('CourseOfAction', secondary=_REL_COA_RELATED_PACKAGESREF, uselist=False)
  exploit_target = relationship('ExploitTarget', uselist=False, secondary=_REL_EXPLOITTARGET_RELATED_PACKAGES)
  incident = relationship('Incident', secondary=_REL_INCIDENT_RELATED_PACKAGES, uselist=False)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_RELATED_PACKAGES)
  threat_actor = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_RELATED_PACKAGES)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_RELATED_PACKAGES)

  _PARENTS = ['campaign', 'exploit_target', 'ttp', 'threat_actor', 'indicator', 'incident', 'coa']

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'relationship':self.convert_value(self.relationship),
                'information_source': self.attribute_to_dict(self.information_source, cache_object),
                'idref': self.convert_value(self.idref),
                'timestamp': self.convert_value(self.timestamp),
               }
    else:
      result = {
                'confidence': self.attribute_to_dict(self.confidence, cache_object),
                'relationship':self.convert_value(self.relationship),
                'idref': self.convert_value(self.idref),
                'timestamp': self.convert_value(self.timestamp),
               }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class RelatedPackage(BaseRelated, Base):
  idref = Column('idref', UnicodeType(255), nullable=False)
  child_id = Column('child_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Event', primaryjoin='RelatedPackage.child_id==Event.identifier', uselist=False)

  _PARENTS = ['event']
  event = relationship('Event', secondary=_REL_EVENT_RELATED_PACKAGES, uselist=False)

  def to_dict(self, cache_object):
    result = {
              'idref': self.convert_value(self.idref),
             }
    parent_dict = BaseRelated.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class RelatedCampaign(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('campaigns.campaign_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Campaign', uselist=False, primaryjoin='RelatedCampaign.child_id==Campaign.identifier')

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_RELATED_CAMPAIGN, uselist=False)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_RELATED_CAMPAIGN)
  _PARENTS = ['campaign', 'indicator']

class RelatedIdentity(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('identitys.identity_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Identity', uselist=False, primaryjoin='RelatedIdentity.child_id==Identity.identifier')

  identity = relationship('Identity', secondary=_REL_IDENTITY_RELATED_IDENTITY, uselist=False)

  _PARENTS = ['identity']

class RelatedIncident(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Incident', uselist=False, primaryjoin='RelatedIncident.child_id==Incident.identifier')

  incident = relationship('Incident', secondary=_REL_INCIDENT_RELATED_INCIDENT, uselist=False)

  _PARENTS = ['incident']

class RelatedIndicator(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Indicator', uselist=False, primaryjoin='RelatedIndicator.child_id==Indicator.identifier')

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_RELATED_INDICATOR, uselist=False)
  incident = relationship('Incident', secondary=_REL_INCIDENT_RELATED_INDICATOR, uselist=False)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_RELATED_INDICATOR)
  _PARENTS = ['campaign', 'indicator', 'incident']

class RelatedThreatActor(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('ThreatActor', uselist=False, primaryjoin='RelatedThreatActor.child_id==ThreatActor.identifier')

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_RELATED_THREATACTOR, uselist=False)
  incident = relationship('Incident', secondary=_REL_INCIDENT_RELATED_THREATACTOR, uselist=False)
  threat_actor = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_RELATED_THREATACTOR)

  _PARENTS = ['threat_actor', 'campaign', 'incident']

class RelatedTTP(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('TTP', uselist=False, primaryjoin='RelatedTTP.child_id==TTP.identifier')

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_RELATED_TTP, uselist=False)
  leveraged_ttp = relationship('LeveragedTTP', secondary=_REL_LEVERAGEDTTP_RELATED_TTP, uselist=False)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_RELATED_TTPS)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_RELATED_TTP)

  _PARENTS = ['campaign', 'ttp', 'indicator', 'leveraged_ttp']

class RelatedCOA(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('CourseOfAction', uselist=False, primaryjoin='RelatedCOA.child_id==CourseOfAction.identifier')
  scope_id = Column('scope_id', Integer, default=None, nullable=False)

  coa = relationship('CourseOfAction', secondary=_REL_COA_RELCOA, uselist=False)

  _PARENTS = ['coa']

  def to_dict(self, cache_object):
    result = {
              'scope_id': self.convert_value(self.scope_id),
             }
    parent_dict = BaseRelated.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
