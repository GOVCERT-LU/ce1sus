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

_REL_THREATACTOR_INFORMATIONSOURCE = Table('rel_threatactor_informationsource', getattr(Base, 'metadata'),

                                       Column('threatactor_id',
                                              BigIntegerType,
                                              ForeignKey('threatactors.threatactor_id',
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

_REL_THREATACTOR_IDENTITY = Table('rel_threatactor_identity', getattr(Base, 'metadata'),

                                  Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                  Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                  )

_REL_THREATACTOR_RELATED_PACKAGES = Table('rel_threatactor_rel_package', getattr(Base, 'metadata'),

                                          Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                          Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                          )

_REL_THREATACTOR_RELATED_THREATACTOR = Table('rel_threatactor_rel_threatactor', getattr(Base, 'metadata'),

                                          Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                          Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                          )

_REL_THREATACTOR_HANDLING = Table('rel_threatactor_handling', getattr(Base, 'metadata'),

                                Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                )

_REL_THREATACTOR_STRUCTUREDTEXT = Table('rel_threatactor_structuredtext', getattr(Base, 'metadata'),

                                       Column('threatactor_id',
                                              BigIntegerType,
                                              ForeignKey('threatactors.threatactor_id',
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

_REL_THREATACTOR_STRUCTUREDTEXT_SHORT = Table('rel_threatactor_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('threatactor_id',
                                              BigIntegerType,
                                              ForeignKey('threatactors.threatactor_id',
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

_REL_THREATACTOR_INTENDED_EFFECT = Table('rel_threatactor_intended_effect', getattr(Base, 'metadata'),

                                      Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                      Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                      )
