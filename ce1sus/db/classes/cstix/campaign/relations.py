# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 20, 2015
"""
from sqlalchemy.sql.schema import Table, Column, ForeignKey

from ce1sus.db.classes.internal.corebase import BigIntegerType
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
