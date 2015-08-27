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

_REL_INCIDENT_INFORMATIONSOURCE = Table('rel_incident_informationsource', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )

_REL_TLE_INIT_LOSSESTIMATION = Table('rel_tle_init_lossestimation', getattr(Base, 'metadata'),

                                     Column('totallossestimation_id',
                                            BigIntegerType,
                                            ForeignKey('totallossestimations.totallossestimation_id',
                                                       ondelete='cascade',
                                                       onupdate='cascade'),
                                            index=True,
                                            nullable=False),
                                     Column('lossestimation_id',
                                            BigIntegerType,
                                            ForeignKey('lossestimations.lossestimation_id',
                                                       ondelete='cascade',
                                                       onupdate='cascade'),
                                            nullable=False,
                                            primary_key=True, index=True)
                                     )

_REL_TLE_ACTU_LOSSESTIMATION = Table('rel_tle_actu_lossestimation', getattr(Base, 'metadata'),

                                     Column('totallossestimation_id',
                                            BigIntegerType,
                                            ForeignKey('totallossestimations.totallossestimation_id',
                                                       ondelete='cascade',
                                                       onupdate='cascade'),
                                            index=True,
                                            nullable=False),
                                     Column('lossestimation_id',
                                            BigIntegerType,
                                            ForeignKey('lossestimations.lossestimation_id',
                                                       ondelete='cascade',
                                                       onupdate='cascade'),
                                            nullable=False,
                                            primary_key=True, index=True)
                                     )

_REL_FMA_DATETIMEWITHPRECISION = Table('rel_fma_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_IC_DATETIMEWITHPRECISION = Table('rel_ic_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_FAE_DATETIMEWITHPRECISION = Table('rel_fae_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_IO_DATETIMEWITHPRECISION = Table('rel_io_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_CA_DATETIMEWITHPRECISION = Table('rel_ca_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_RA_DATETIMEWITHPRECISION = Table('rel_ra_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_IR_DATETIMEWITHPRECISION = Table('rel_ir_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_ICL_DATETIMEWITHPRECISION = Table('rel_icl_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('time_id',
                                                     BigIntegerType,
                                                     ForeignKey('stixtimes.time_id',
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

_REL_PROPERTYAFFECTED_STRUCTUREDTEXT = Table('rel_propertyaffected_structuredtext', getattr(Base, 'metadata'),

                                             Column('propertyaffected_id',
                                                    BigIntegerType,
                                                    ForeignKey('propertyaffecteds.propertyaffected_id',
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

_REL_INCIDENT_HANDLING = Table('rel_incident_handling', getattr(Base, 'metadata'),

                                    Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INCIDENT_IDENTITY = Table('rel_incident_identity', getattr(Base, 'metadata'),

                               Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                               Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                               )

_REL_INCIDENT_RELATED_THREATACTOR = Table('rel_incident_rel_threatactor', getattr(Base, 'metadata'),

                                          Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                          Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                          )

_REL_INCIDENT_RELATED_INDICATOR = Table('rel_incident_rel_indicator', getattr(Base, 'metadata'),

                                        Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                        Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                        )

_REL_INCIDENT_RELATED_OBSERVABLE = Table('rel_incident_rel_observable', getattr(Base, 'metadata'),

                                         Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                         Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                         )

_REL_INCIDENT_RELATED_INCIDENT = Table('rel_incident_rel_incident', getattr(Base, 'metadata'),

                                       Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                       Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                       )

_REL_INCIDENT_RELATED_PACKAGES = Table('rel_incident_relpackage_ref', getattr(Base, 'metadata'),

                                       Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                       Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                       )

_REL_LEVERAGEDTTP_RELATED_TTP = Table('rel_leveragedttp_rel_ttp', getattr(Base, 'metadata'),

                                      Column('leveragedttp_id', BigIntegerType, ForeignKey('leveragedttps.leveragedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                      Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                      )

_REL_INCIDENT_INFORMATIONSOURCE_REP = Table('rel_incident_informationsource_rep', getattr(Base, 'metadata'),

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
                                                   primary_key=True, index=True)
                                            )

_REL_INCIDENT_INFORMATIONSOURCE_RES = Table('rel_incident_informationsource_res', getattr(Base, 'metadata'),

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
                                                   primary_key=True, index=True)
                                            )

_REL_INCIDENT_INFORMATIONSOURCE_COO = Table('rel_incident_informationsource_coo', getattr(Base, 'metadata'),

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
                                                   primary_key=True, index=True)
                                            )
_REL_INCIDENT_COATAKEN = Table('rel_incident_coataken', getattr(Base, 'metadata'),

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
                                                   primary_key=True, index=True)
                                            )
_REL_INCIDENT_COAREQUESTED = Table('rel_incident_coarequested', getattr(Base, 'metadata'),

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
                                                   primary_key=True, index=True)
                                            )

_REL_INCIDENT_STRUCTUREDTEXT = Table('rel_incident_structuredtext', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )


_REL_INCIDENT_STRUCTUREDTEXT_SHORT = Table('rel_incident_structuredtext_short', getattr(Base, 'metadata'),

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
                                              primary_key=True, index=True)
                                       )

_REL_INCIDENT_CONFIDENCE = Table('rel_incident_confidence', getattr(Base, 'metadata'),

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
                                                     primary_key=True, index=True)
                                              )

_REL_INCIDENT_INTENDED_EFFECT = Table('rel_incident_intended_effect', getattr(Base, 'metadata'),

                                      Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                      Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                      )

_REL_HISTORYITEM_COATAKEN = Table('rel_historyitem_coataken', getattr(Base, 'metadata'),

                                    Column('coataken_id',
                                           BigIntegerType,
                                           ForeignKey('coatakens.coataken_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('historyitem_id',
                                           BigIntegerType,
                                           ForeignKey('historyitems.historyitem_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           primary_key=True, index=True)
                                    )

_REL_COATAKEN_COA = Table('rel_coataken_courseofaction', getattr(Base, 'metadata'),

                          Column('coataken_id',
                                 BigIntegerType,
                                 ForeignKey('coatakens.coataken_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 index=True,
                                 nullable=False),
                          Column('structuredtext_id',
                                 BigIntegerType,
                                 ForeignKey('courseofactions.courseofaction_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 nullable=False,
                                 primary_key=True, index=True)
                          )

_REL_COAREQUESTED_COA = Table('rel_coarequested_courseofaction', getattr(Base, 'metadata'),

                          Column('coarequested_id',
                                 BigIntegerType,
                                 ForeignKey('coarequesteds.coarequested_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 index=True,
                                 nullable=False),
                          Column('structuredtext_id',
                                 BigIntegerType,
                                 ForeignKey('courseofactions.courseofaction_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 nullable=False,
                                 primary_key=True, index=True)
                          )

_REL_COATIME_DATETIME_START = Table('rel_coatime_datetime_start', getattr(Base, 'metadata'),

                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
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

_REL_COATIME_DATETIME_ENDED = Table('rel_coatime_datetime_end', getattr(Base, 'metadata'),

                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
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

_REL_COATAKEN_COATIME = Table('rel_coataken_coatime', getattr(Base, 'metadata'),

                                    Column('coataken_id',
                                           BigIntegerType,
                                           ForeignKey('coatakens.coataken_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           primary_key=True, index=True)
                                    )

_REL_COAREQUESTED_COATIME = Table('rel_coarequested_coatime', getattr(Base, 'metadata'),

                                    Column('coarequested_id',
                                           BigIntegerType,
                                           ForeignKey('coarequesteds.coarequested_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           primary_key=True, index=True)
                                    )

_REL_AFFECTEDASSET_STRUCTUREDTEXT = Table('rel_affectedasset_structuredtext', getattr(Base, 'metadata'),

                                       Column('affectedasset_id',
                                              BigIntegerType,
                                              ForeignKey('affectedassets.affectedasset_id',
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

_REL_AFFECTEDASSET_BFR_STRUCTUREDTEXT = Table('rel_affectedasset_bfr_structuredtext', getattr(Base, 'metadata'),

                                       Column('affectedasset_id',
                                              BigIntegerType,
                                              ForeignKey('affectedassets.affectedasset_id',
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
