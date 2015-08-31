# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 2, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.campaign.relations import _REL_CAMPAIGN_NAME, _REL_CAMPAIGN_INTENDEDEFFECT, _REL_CAMPAIGN_HANDLING, _REL_CAMPAIGN_RELATED_TTP, \
  _REL_CAMPAIGN_RELATED_INDICATOR, _REL_CAMPAIGN_RELATED_THREATACTOR, _REL_CAMPAIGN_RELATED_CAMPAIGN, _REL_CAMPAIGN_CONFIDENCE, _REL_CAMPAIGN_RELATED_PACKAGES
from ce1sus.db.classes.cstix.common.activity import Activity
from ce1sus.db.classes.cstix.common.intended_effect import IntendedEffect
from ce1sus.db.classes.cstix.common.names import Name
from ce1sus.db.classes.cstix.common.vocabs import CampaignStatus
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Campaign(BaseCoreComponent, Base):

  names = relationship(Name, secondary=_REL_CAMPAIGN_NAME)
  intended_effects_instances = relationship(IntendedEffect, secondary=_REL_CAMPAIGN_INTENDEDEFFECT)
  status_id = Column('status_id', Integer)
  handling = relationship(MarkingSpecification, secondary=_REL_CAMPAIGN_HANDLING)

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

  related_ttps = relationship('RelatedTTP', secondary=_REL_CAMPAIGN_RELATED_TTP)
  # TODO: related_incidents
  # related_incidents = RelatedIncidents()
  related_indicators = relationship('RelatedIndicator', secondary=_REL_CAMPAIGN_RELATED_INDICATOR)
  attribution = relationship('RelatedThreatActor', secondary=_REL_CAMPAIGN_RELATED_THREATACTOR)
  # TODO: associated_campaigns = relatedCampaign
  associated_campaigns = relationship('RelatedCampaign', secondary=_REL_CAMPAIGN_RELATED_CAMPAIGN)

  confidence = relationship('Confidence', secondary=_REL_CAMPAIGN_CONFIDENCE)
  activity = relationship(Activity)
  related_packages = relationship('RelatedPackageRef', secondary=_REL_CAMPAIGN_RELATED_PACKAGES)
  related_campaign = relationship('RelatedCampaign', primaryjoin='RelatedCampaign.child_id==Campaign.identifier', uselist=False)

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['event', 'related_campaign']
  event = relationship('Event', uselist=False)

  def to_dict(self, cache_object):
    confidence = self.attribute_to_dict(self.confidence, cache_object)
    handling = self.attributelist_to_dict('handling', cache_object)
    names = self.attributelist_to_dict('names', cache_object)
    if cache_object.complete:
      activity = self.attributelist_to_dict('activity', cache_object)
      associated_campaigns = self.attributelist_to_dict('associated_campaigns', cache_object)
      attribution = self.attributelist_to_dict('attribution', cache_object)
      intended_effects_instances = self.attributelist_to_dict('intended_effects_instances', cache_object)
      related_indicators = self.attributelist_to_dict('related_indicators', cache_object)
      related_packages = self.attributelist_to_dict('related_packages', cache_object)
      related_ttps = self.attributelist_to_dict('related_ttps', cache_object)
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
