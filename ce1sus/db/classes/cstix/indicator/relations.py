# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 21, 2015
"""
from sqlalchemy.sql.schema import Table, Column, ForeignKey

from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_SIGHTING_REL_OBSERVABLE = Table('rel_sigthing_rel_observable', getattr(Base, 'metadata'),

                                        Column('sighting_id', BigIntegerType, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                        Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_SIGHTING_STRUCTUREDTEXT = Table('rel_sighting_structuredtext', getattr(Base, 'metadata'),

                                       Column('sighting_id',
                                              BigIntegerType,
                                              ForeignKey('sightings.sighting_id',
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
                                              primary_key=True, index=True)
                                       )

_REL_SIGHTING_CONFIDENCE = Table('rel_sighting_confidence', getattr(Base, 'metadata'),

                                        Column('sighting_id', BigIntegerType, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_SIGHTING_INFORMATIONSOURCE = Table('rel_sighting_informationsource', getattr(Base, 'metadata'),

                                       Column('sighting_id',
                                              BigIntegerType,
                                              ForeignKey('sightings.sighting_id',
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
                                              primary_key=True, index=True)
                                       )

_REL_INDICATOR_KILLCHAINPHASEREF = Table('rel_indicator_killchainphase_ref', getattr(Base, 'metadata'),

                                      Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                      Column('killchainphasereference_id', BigIntegerType, ForeignKey('killchainphasereferences.killchainphasereference_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                      )

_REL_INDICATOR_OBSERVABLE = Table('rel_indicator_observable', getattr(Base, 'metadata'),

                                  Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                  Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                  )

_REL_INDICATOR_RELATED_TTPS = Table('rel_indicator_related_ttps', getattr(Base, 'metadata'),

                                    Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INDICATOR_RELATED_PACKAGES = Table('rel_indicator_relpackage_ref', getattr(Base, 'metadata'),

                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                        Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_INDICATOR_RELATED_INDICATOR = Table('rel_indicator_related_indicators', getattr(Base, 'metadata'),

                                         Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                         Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                         )

_REL_INDICATOR_RELATED_CAMPAIGN = Table('rel_indicator_rel_indicator', getattr(Base, 'metadata'),

                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_INDICATOR_HANDLING = Table('rel_indicator_handling', getattr(Base, 'metadata'),

                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_INDICATOR_CONFIDENCE = Table('rel_indicator_confidence', getattr(Base, 'metadata'),

                                        Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_INDICATOR_STRUCTUREDTEXT = Table('rel_indicator_structuredtext', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )

_REL_INDICATOR_STRUCTUREDTEXT_SHORT = Table('rel_indicator_structuredtext_short', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )

_REL_INDICAOTR_INFORMATIONSOURCE = Table('rel_indicator_informationsource', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )

_REL_INDICATOR_STATEMENT = Table('rel_indicator_statement', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )

_REL_TESTMECHANISM_INFORMATIONSOURCE = Table('rel_basetestmechanism_informationsource', getattr(Base, 'metadata'),

                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
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
                                              primary_key=True, index=True)
                                       )

_REL_TESTMECHANISM_STATEMENT = Table('rel_basetestmechanism_statement', getattr(Base, 'metadata'),

                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
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
                                              primary_key=True, index=True)
                                       )

_REL_TESTMECHANISM_STRUCTUREDTEXT = Table('rel_testmechanism_structuredtext', getattr(Base, 'metadata'),

                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
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
                                              primary_key=True, index=True)
                                       )

_REL_TESTMECHANISM_VOCABSTRING = Table('rel_testmechanism_statement', getattr(Base, 'metadata'),

                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('vocabstring_id',
                                             BigIntegerType,
                                             ForeignKey('vocabstrings.vocabstring_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              primary_key=True, index=True)
                                       )
