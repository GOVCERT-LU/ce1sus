# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.activity import Activity
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.intended_effect import IntendedEffect
from ce1sus.db.classes.cstix.common.names import Name
from ce1sus.db.classes.cstix.common.related import RelatedIndicator, RelatedPackageRef, RelatedThreatActor, RelatedTTP, RelatedCampaign
from ce1sus.db.classes.cstix.common.vocabs import CampaignStatus
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_CAMPAIGN_HANDLING = Table('rel_campaign_handling', getattr(Base, 'metadata'),
                                Column('rth_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                )

_REL_CAMPAIGN_RELATED_INDICATOR = Table('rel_campaign_related_indicators', getattr(Base, 'metadata'),
                                        Column('rcr_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                        )

_REL_CAMPAIGN_RELATED_PACKAGES = Table('rel_campaign_rel_package', getattr(Base, 'metadata'),
                                       Column('rcr_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                       Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )

_REL_CAMPAIGN_RELATED_THREATACTOR = Table('rel_campaign_rel_threatactor', getattr(Base, 'metadata'),
                                          Column('rcr_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                          Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                          Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                          )

_REL_CAMPAIGN_RELATED_TTP = Table('rel_campaign_rel_ttp', getattr(Base, 'metadata'),
                                  Column('rct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                  Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_CAMPAIGN_RELATED_CAMPAIGN = Table('rel_campaign_rel_campagin', getattr(Base, 'metadata'),
                                       Column('rct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                       Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )

_REL_CAMPAIGN_NAME = Table('rel_campaign_names', getattr(Base, 'metadata'),
                           Column('rct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                           Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                           Column('name_id', BigIntegerType, ForeignKey('names.name_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                           )

_REL_CAMPAIGN_INTENDEDEFFECT = Table('rel_campaign_intendedeffect', getattr(Base, 'metadata'),
                           Column('rcie_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                           Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                           Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                           )

_REL_CAMPAIGN_CONFIDENCE = Table('rel_campaign_confidence', getattr(Base, 'metadata'),
                                        Column('ric_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                        Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False,)
                                        )

_REL_CAMPAIGN_STRUCTUREDTEXT = Table('rel_campaign_structuredtext', getattr(Base, 'metadata'),
                                       Column('rcst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('campaign_id',
                                              BigIntegerType,
                                              ForeignKey('campaigns.campaign_id',
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

_REL_CAMPAIGN_STRUCTUREDTEXT_SHORT = Table('rel_campaign_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rcst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('campaign_id',
                                              BigIntegerType,
                                              ForeignKey('campaigns.campaign_id',
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

class Campaign(BaseCoreComponent, Base):

  names = relationship(Name, secondary=_REL_CAMPAIGN_NAME, backref='campaign')
  intended_effects_instances = relationship(IntendedEffect, secondary=_REL_CAMPAIGN_INTENDEDEFFECT, backref='campaign')
  status_id = Column('status_id', Integer)
  handling = relationship(MarkingSpecification, secondary=_REL_CAMPAIGN_HANDLING, backref='campaign')

  __status = None

  @property
  def status(self):
    if not self.__status:
      if self.status_id:
        self.__status = CampaignStatus(self, 'status_id')
    return self.__status
  
  @status.setter
  def status(self, value):
    if not self.status:
      self.__status = CampaignStatus(self, 'status_id')
    self.status.name = value

  related_ttps = relationship(RelatedTTP, secondary=_REL_CAMPAIGN_RELATED_TTP, backref='campaign')
  # TODO: related_incidents
  # related_incidents = RelatedIncidents()
  related_indicators = relationship(RelatedIndicator, secondary=_REL_CAMPAIGN_RELATED_INDICATOR, backref='campaign')
  attribution = relationship(RelatedThreatActor, secondary=_REL_CAMPAIGN_RELATED_THREATACTOR, backref='campaign')
  # TODO: associated_campaigns = relatedCampaign
  associated_campaigns = relationship(RelatedCampaign, secondary=_REL_CAMPAIGN_RELATED_CAMPAIGN, backref='campaign')

  confidence = relationship(Confidence, secondary=_REL_CAMPAIGN_CONFIDENCE, backref='campaign')
  activity = relationship(Activity, backref='campaign')
  related_packages = relationship(RelatedPackageRef, secondary=_REL_CAMPAIGN_RELATED_PACKAGES, backref='campaign')

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @property
  def parent(self):
    if self.event:
      return self.event
    elif self.related_campaign:
      return self.related_campaign
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):
    confidence = self.attribute_to_dict(self.confidence, cache_object)
    handling = self.attributelist_to_dict(self.handling, cache_object)
    names = self.attributelist_to_dict(self.names, cache_object)
    if cache_object.complete:
      activity = self.attributelist_to_dict(self.activity, cache_object)
      associated_campaigns = self.attributelist_to_dict(self.associated_campaigns, cache_object)
      attribution = self.attributelist_to_dict(self.attribution, cache_object)
      intended_effects_instances = self.attributelist_to_dict(self.intended_effects_instances, cache_object)
      related_indicators = self.attributelist_to_dict(self.related_indicators, cache_object)
      related_packages = self.attributelist_to_dict(self.related_packages, cache_object)
      related_ttps = self.attributelist_to_dict(self.related_ttps, cache_object)
      result = {'confidence': confidence,
                'handling': handling,
                'names': names,
                'activity':activity,
                'associated_campaigns':associated_campaigns,
                'attribution':attribution,
                'intended_effects_instances':intended_effects_instances,
                'related_indicators':related_indicators,
                'related_packages':related_packages,
                'related_ttps':related_ttps
                }
    else:
      result = {'confidence': confidence,
                'handling': handling,
                'names': names,
                }
    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
