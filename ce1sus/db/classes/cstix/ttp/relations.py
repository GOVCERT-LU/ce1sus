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

_REL_TTP_INFORMATIONSOURCE = Table('rel_ttp_informationsource', getattr(Base, 'metadata'),

                                       Column('ttp_id',
                                              BigIntegerType,
                                              ForeignKey('ttps.ttp_id',
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

_REL_VICTIMTARGETING_IDENTITY = Table('rel_victimtargeting_identity', getattr(Base, 'metadata'),

                                       Column('victimtargeting_id', BigIntegerType, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                       Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                       )


_REL_TTP_HANDLING = Table('rel_ttp_handling', getattr(Base, 'metadata'),

                                Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                )

_REL_TTP_KILLCHAINPHASE = Table('rel_ttp_killchainphase', getattr(Base, 'metadata'),

                                      Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                      Column('killchainphasereference_id', BigIntegerType, ForeignKey('killchainphasereferences.killchainphasereference_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                      )

_REL_TTP_RELATED_PACKAGES = Table('rel_ttp_rel_package', getattr(Base, 'metadata'),

                                  Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                  Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                  )

_REL_TTP_RELATED_TTP = Table('rel_ttp_rel_ttp', getattr(Base, 'metadata'),

                                  Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                  Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                  )

_REL_TTP_RELATED_EXPLOITTARGET = Table('rel_ttp_rel_exploittarget', getattr(Base, 'metadata'),

                                  Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                  Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                  )

_REL_TTP_STRUCTUREDTEXT = Table('rel_ttp_structuredtext', getattr(Base, 'metadata'),

                                       Column('ttp_id',
                                              BigIntegerType,
                                              ForeignKey('ttps.ttp_id',
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

_REL_TTP_STRUCTUREDTEXT_SHORT = Table('rel_ttp_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('ttp_id',
                                              BigIntegerType,
                                              ForeignKey('ttps.ttp_id',
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

_REL_TTP_INTENDED_EFFECT = Table('rel_ttp_intended_effect', getattr(Base, 'metadata'),

                                      Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                      Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                      )

_REL_MALWAREINSTANCE_STRUCTUREDTEXT = Table('rel_malwareinstance_structuredtext', getattr(Base, 'metadata'),

                                       Column('malwareinstance_id',
                                              BigIntegerType,
                                              ForeignKey('malwareinstances.malwareinstance_id',
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

_REL_MALWAREINSTANCE_STRUCTUREDTEXT_SHORT = Table('rel_malwareinstance_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('malwareinstance_id',
                                              BigIntegerType,
                                              ForeignKey('malwareinstances.malwareinstance_id',
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

_REL_INFRASTRUCTURE_STRUCTUREDTEXT = Table('rel_infrastructure_structuredtext', getattr(Base, 'metadata'),

                                       Column('infrastructure_id',
                                              BigIntegerType,
                                              ForeignKey('infrastructures.infrastructure_id',
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

_REL_INFRASTRUCTURE_STRUCTUREDTEXT_SHORT = Table('rel_infrastructure_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('infrastructure_id',
                                              BigIntegerType,
                                              ForeignKey('infrastructures.infrastructure_id',
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

_REL_EXPLOIT_STRUCTUREDTEXT = Table('rel_exploit_structuredtext', getattr(Base, 'metadata'),

                                       Column('exploit_id',
                                              BigIntegerType,
                                              ForeignKey('exploits.exploit_id',
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

_REL_EXPLOIT_STRUCTUREDTEXT_SHORT = Table('rel_exploit_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('exploit_id',
                                              BigIntegerType,
                                              ForeignKey('exploits.exploit_id',
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

_REL_ATTACKPATTERN_STRUCTUREDTEXT = Table('rel_attackpattern_structuredtext', getattr(Base, 'metadata'),

                                       Column('attackpattern_id',
                                              BigIntegerType,
                                              ForeignKey('attackpatterns.attackpattern_id',
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

_REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT = Table('rel_attackpattern_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('attackpattern_id',
                                              BigIntegerType,
                                              ForeignKey('attackpatterns.attackpattern_id',
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
