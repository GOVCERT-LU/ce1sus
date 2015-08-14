# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from datetime import datetime
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import DateTime, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_RELATEDOBSERVABLE_CONFIDENCE = Table('rel_relatedobservable_confidence', getattr(Base, 'metadata'),
                                          Column('rroc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                          Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                          Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                          )

_REL_RELATEDEXPLOITTARGET_CONFIDENCE = Table('rel_relatedexploittarget_confidence', getattr(Base, 'metadata'),
                                             Column('rretc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                             Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                             Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                             )

_REL_RELATEDPACKAGEREF_CONFIDENCE = Table('rel_relatedpackageref_confidence', getattr(Base, 'metadata'),
                                          Column('rrprc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                          Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                          Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                          )

_REL_RELATEDPACKAGE_CONFIDENCE = Table('rel_relatedpackage_confidence', getattr(Base, 'metadata'),
                                       Column('rrpc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                       Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )

_REL_RELATEDCAMPAIGN_CONFIDENCE = Table('rel_relatedcampaign_confidence', getattr(Base, 'metadata'),
                                        Column('rrcc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_RELATEDCOA_CONFIDENCE = Table('rel_relatedcoa_confidence', getattr(Base, 'metadata'),
                                        Column('rrcc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('relatedcoa_id', BigIntegerType, ForeignKey('relatedcoas.relatedcoa_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_RELATEDIDENTITY_CONFIDENCE = Table('rel_relatedidentity_confidence', getattr(Base, 'metadata'),
                                        Column('rric_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_RELATEDINDICATOR_CONFIDENCE = Table('rel_relatedindicator_confidence', getattr(Base, 'metadata'),
                                         Column('rric_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                         Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                         Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                         )

_REL_RELATEDINCIDENT_CONFIDENCE = Table('rel_relatedincident_confidence', getattr(Base, 'metadata'),
                                         Column('rric_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                         Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                         Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                         )

_REL_RELATEDTHREATACTOR_CONFIDENCE = Table('rel_relatedthreatactor_confidence', getattr(Base, 'metadata'),
                                           Column('rrtac_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                           Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                           Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                           )

_REL_RELATEDTTP_CONFIDENCE = Table('rel_relatedttp_confidence', getattr(Base, 'metadata'),
                                   Column('rrtc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDPACKAGEREF_INFORMATIONSOURCE = Table('rel_relatedpackageref_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrpis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDPACKAGE_INFORMATIONSOURCE = Table('rel_relatedpackage_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrpis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDINDICATOR_INFORMATIONSOURCE = Table('rel_relatedindicator_infromationsource', getattr(Base, 'metadata'),
                                   Column('rriis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDINCIDENT_INFORMATIONSOURCE = Table('rel_relatedincident_infromationsource', getattr(Base, 'metadata'),
                                   Column('rriis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDEXPLOITTARGET_INFORMATIONSOURCE = Table('rel_relatedexploittarget_infromationsource', getattr(Base, 'metadata'),
                                   Column('rretis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDOBSERVABLE_INFORMATIONSOURCE = Table('rel_relatedobservable_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrois_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDTHREATACTOR_INFORMATIONSOURCE = Table('rel_relatedthreatactor_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrtais_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDCOA_INFORMATIONSOURCE = Table('rel_relatedcoa_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrcoais_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedcoa_id', BigIntegerType, ForeignKey('relatedcoas.relatedcoa_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDTTP_INFORMATIONSOURCE = Table('rel_relatedttp_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrttpis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDCAMPAIGN_INFORMATIONSOURCE = Table('rel_relatedcampaign_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrcis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

_REL_RELATEDIDENTITY_INFORMATIONSOURCE = Table('rel_relatedidentity_infromationsource', getattr(Base, 'metadata'),
                                   Column('rrcis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                   Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                   )

class BaseRelated(Entity):

  @declared_attr
  def confidence(self):
    return relationship(Confidence, secondary='rel_{0}_confidence'.format(self.get_classname().lower()), uselist=False, backref='related_{0}'.format(self.get_classname().lower()))

  relationship = Column('relationship', UnicodeType(255))

  @declared_attr
  def information_source(self):
    return relationship('InformationSource', secondary='rel_{0}_infromationsource'.format(self.get_classname().lower()), uselist=False, backref='related_{0}'.format(self.get_classname().lower()))

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
  child = relationship('Observable', primaryjoin='RelatedObservable.child_id==Observable.identifier', uselist=False, backref='related_observable')

  _PARENTS = ['sigthing', 'incident']

  def validate(self):
    # TODO: validate
    return True


class RelatedExploitTarget(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('exploittargets.exploittarget_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('ExploitTarget', uselist=False, primaryjoin='RelatedExploitTarget.child_id==ExploitTarget.identifier', backref='related_exploit_target')

  _PARENTS = ['victim_targeting', 'ttp']

class RelatedPackageRef(BaseRelated, Base):
  idref = Column('idref', UnicodeType(255), nullable=False)
  timestamp = Column('timestamp', DateTime, default=datetime.utcnow())

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
  child = relationship('Event', primaryjoin='RelatedPackage.child_id==Event.identifier', uselist=False, backref='related_package')

  _PARENTS = ['event']

  def to_dict(self, cache_object):
    result = {
              'idref': self.convert_value(self.idref),
             }
    parent_dict = BaseRelated.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class RelatedCampaign(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('campaigns.campaign_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Campaign', uselist=False, primaryjoin='RelatedCampaign.child_id==Campaign.identifier', backref='related_campaign')

  _PARENTS = ['campaign', 'indicator']

class RelatedIdentity(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('identitys.identity_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Identity', uselist=False, primaryjoin='RelatedIdentity.child_id==Identity.identifier', backref='related_identity')

  _PARENTS = ['identity']

class RelatedIncident(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Incident', uselist=False, primaryjoin='RelatedIncident.child_id==Incident.identifier', backref='related_incident')

  _PARENTS = ['incident']

class RelatedIndicator(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('Indicator', uselist=False, primaryjoin='RelatedIndicator.child_id==Indicator.identifier', backref='related_indicator')

  _PARENTS = ['campaign', 'indicator', 'incident']

class RelatedThreatActor(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('ThreatActor', uselist=False, primaryjoin='RelatedThreatActor.child_id==ThreatActor.identifier', backref='related_threat_actor')

  _PARENTS = ['threat_actor', 'campaign', 'incident']

class RelatedTTP(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('TTP', uselist=False, primaryjoin='RelatedTTP.child_id==TTP.identifier', backref='related_ttp')

  _PARENTS = ['campaign', 'ttp', 'indicator', 'leveraged_ttp']

class RelatedCOA(BaseRelated, Base):
  child_id = Column('child_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child = relationship('CourseOfAction', uselist=False, primaryjoin='RelatedCOA.child_id==CourseOfAction.identifier', backref='related_coa')
  scope_id = Column('scope_id', Integer, default=None, nullable=False)

  _PARENTS = ['coa']

  def to_dict(self, cache_object):
    result = {
              'scope_id': self.convert_value(self.scope_id),
             }
    parent_dict = BaseRelated.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
