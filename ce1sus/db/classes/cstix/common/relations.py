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

_REL_RELATEDOBSERVABLE_CONFIDENCE = Table('rel_relatedobservable_confidence', getattr(Base, 'metadata'),

                                          Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                          Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                          )

_REL_RELATEDEXPLOITTARGET_CONFIDENCE = Table('rel_relatedexploittarget_confidence', getattr(Base, 'metadata'),

                                             Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                             Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                             )

_REL_RELATEDPACKAGEREF_CONFIDENCE = Table('rel_relatedpackageref_confidence', getattr(Base, 'metadata'),

                                          Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                          Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                          )

_REL_RELATEDPACKAGE_CONFIDENCE = Table('rel_relatedpackage_confidence', getattr(Base, 'metadata'),

                                       Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                       Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                       )

_REL_RELATEDCAMPAIGN_CONFIDENCE = Table('rel_relatedcampaign_confidence', getattr(Base, 'metadata'),

                                        Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_RELATEDCOA_CONFIDENCE = Table('rel_relatedcoa_confidence', getattr(Base, 'metadata'),

                                        Column('relatedcoa_id', BigIntegerType, ForeignKey('relatedcoas.relatedcoa_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_RELATEDIDENTITY_CONFIDENCE = Table('rel_relatedidentity_confidence', getattr(Base, 'metadata'),

                                        Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                        Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_RELATEDINDICATOR_CONFIDENCE = Table('rel_relatedindicator_confidence', getattr(Base, 'metadata'),

                                         Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                         Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                         )

_REL_RELATEDINCIDENT_CONFIDENCE = Table('rel_relatedincident_confidence', getattr(Base, 'metadata'),

                                         Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                         Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                         )

_REL_RELATEDTHREATACTOR_CONFIDENCE = Table('rel_relatedthreatactor_confidence', getattr(Base, 'metadata'),

                                           Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                           Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                           )

_REL_RELATEDTTP_CONFIDENCE = Table('rel_relatedttp_confidence', getattr(Base, 'metadata'),

                                   Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDPACKAGEREF_INFORMATIONSOURCE = Table('rel_relatedpackageref_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDPACKAGE_INFORMATIONSOURCE = Table('rel_relatedpackage_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDINDICATOR_INFORMATIONSOURCE = Table('rel_relatedindicator_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDINCIDENT_INFORMATIONSOURCE = Table('rel_relatedincident_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDEXPLOITTARGET_INFORMATIONSOURCE = Table('rel_relatedexploittarget_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDOBSERVABLE_INFORMATIONSOURCE = Table('rel_relatedobservable_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDTHREATACTOR_INFORMATIONSOURCE = Table('rel_relatedthreatactor_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDCOA_INFORMATIONSOURCE = Table('rel_relatedcoa_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedcoa_id', BigIntegerType, ForeignKey('relatedcoas.relatedcoa_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDTTP_INFORMATIONSOURCE = Table('rel_relatedttp_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDCAMPAIGN_INFORMATIONSOURCE = Table('rel_relatedcampaign_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )

_REL_RELATEDIDENTITY_INFORMATIONSOURCE = Table('rel_relatedidentity_infromationsource', getattr(Base, 'metadata'),

                                   Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                   Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                   )


_REL_TOOLINFORMATION_STRUCTUREDTEXT = Table('rel_toolinformation_structuredtext', getattr(Base, 'metadata'),

                                              Column('toolinformation_id',
                                                     BigIntegerType,
                                                     ForeignKey('toolinformations.toolinformation_id',
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
                                                     primary_key=True, index=True))

_REL_TOOLINFORMATION_STRUCTUREDTEXT_SHORT = Table('rel_toolinformation_structuredtextshort', getattr(Base, 'metadata'),

                                              Column('toolinformation_id',
                                                     BigIntegerType,
                                                     ForeignKey('toolinformations.toolinformation_id',
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
                                                     primary_key=True, index=True))

_REL_ACTIVITY_STRUCTUREDTEXT = Table('rel_activity_structuredtext', getattr(Base, 'metadata'),

                                     Column('activity_id',
                                            BigIntegerType,
                                            ForeignKey('activitys.activity_id',
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

_REL_ACTIVITY_DATETIMEWITHPRECISION = Table('rel_activity_datetimewithprecision', getattr(Base, 'metadata'),

                                            Column('activity_id',
                                                   BigIntegerType,
                                                   ForeignKey('activitys.activity_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   index=True,
                                                   nullable=False),
                                            Column('datetimewithprecision_id',
                                                   BigIntegerType,
                                                   ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   nullable=False,
                                                   primary_key=True, index=True)
                                            )

_REL_CONFIDENCE_STRUCTUREDTEXT = Table('rel_confidence_structuredtext', getattr(Base, 'metadata'),

                                       Column('confidence_id',
                                              BigIntegerType,
                                              ForeignKey('confidences.confidence_id',
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

_REL_CONFIDENCE_INFORMATIONSOURCE = Table('rel_confidence_informationsource', getattr(Base, 'metadata'),

                                       Column('confidence_id',
                                              BigIntegerType,
                                              ForeignKey('confidences.confidence_id',
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

_REL_IDENTITY_RELATED_IDENTITY = Table('rel_identity_rel_identity', getattr(Base, 'metadata'),

                                       Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                       Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                       )

_REL_INFORMATIONSOURCE_IDENTITY = Table('rel_informationsource_identity', getattr(Base, 'metadata'),

                                  Column('informationsource_id',
                                         BigIntegerType,
                                         ForeignKey('informationsources.informationsource_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         primary_key=True, index=True),
                                  Column('identity_id',
                                         BigIntegerType,
                                         ForeignKey('identitys.identity_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         primary_key=True, index=True)
                                  )

_REL_INFORMATIONSOURCE_TOOL = Table('rel_informationsource_tool', getattr(Base, 'metadata'),

                                    Column('informationsource_id',
                                           BigIntegerType,
                                           ForeignKey('informationsources.informationsource_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           nullable=False,
                                           primary_key=True, index=True),
                                    Column('toolinformation_id',
                                           BigIntegerType,
                                           ForeignKey('toolinformations.toolinformation_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           nullable=False,
                                           primary_key=True, index=True)
                                    )

_REL_INFORMATIONSOURCE_INFORMATIONSOURCE = Table('rel_informationsource_contributing_sources', getattr(Base, 'metadata'),

                                  Column('parent_id',
                                         BigIntegerType,
                                         ForeignKey('informationsources.informationsource_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         primary_key=True, index=True),
                                  Column('child_id',
                                         BigIntegerType,
                                         ForeignKey('informationsources.informationsource_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         primary_key=True, index=True)
                                  )

_REL_INFORMATIONSOURCE_STRUCTUREDTEXT = Table('rel_informationsource_structuredtext', getattr(Base, 'metadata'),

                                              Column('informationsource_id',
                                                     BigIntegerType,
                                                     ForeignKey('informationsources.informationsource_id',
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


_REL_STATEMENT_STRUCTUREDTEXT = Table('rel_statement_structuredtext', getattr(Base, 'metadata'),

                                      Column('statement_id',
                                             BigIntegerType,
                                             ForeignKey('statements.statement_id',
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

_REL_STATEMENT_INFORMATIONSOURCE = Table('rel_statement_informationsource', getattr(Base, 'metadata'),

                                         Column('statement_id',
                                                BigIntegerType,
                                                ForeignKey('statements.statement_id',
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

_REL_STATEMENT_CONFIDENCE = Table('rel_statement_confidence', getattr(Base, 'metadata'),

                                  Column('statement_id',
                                         BigIntegerType,
                                         ForeignKey('statements.statement_id',
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
                                         primary_key=True, index=True)
                                  )

