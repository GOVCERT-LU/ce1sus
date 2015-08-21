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

_REL_STIXHEADER_STRUCTUREDTEXT = Table('rel_stixheader_structuredtext', getattr(Base, 'metadata'),
                                       Column('rtstixheaderst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('stixheader_id',
                                              BigIntegerType,
                                              ForeignKey('stixheaders.stixheader_id',
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

_REL_STIXHEADER_STRUCTUREDTEXT_SHORT = Table('rel_stixheader_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rtstixheaderst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('stixheader_id',
                                              BigIntegerType,
                                              ForeignKey('stixheaders.stixheader_id',
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

_REL_STIXHEADER_INFORMATIONSOURCE = Table('rel_stixheader_informationsource', getattr(Base, 'metadata'),
                                       Column('rstixheaderis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('stixheader_id',
                                              BigIntegerType,
                                              ForeignKey('stixheaders.stixheader_id',
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
                                              index=True)
                                       )

_REL_STIXHEADER_HANDLING = Table('rel_stixheader_handling', getattr(Base, 'metadata'),
                            Column('eih_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                            Column('stixheader_id', BigIntegerType, ForeignKey('stixheaders.stixheader_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                            Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                            )
