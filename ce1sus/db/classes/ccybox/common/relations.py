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


_REL_STARTTIME_DATETIMEWITHPRECISION = Table('rel_starttime_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     index=True,
                                                     primary_key=True,
                                                     nullable=False),
                                              Column('datetimewithprecision_id',
                                                     BigIntegerType,
                                                     ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     primary_key=True,
                                                     nullable=False,
                                                     index=True)
                                              )

_REL_ENDTIME_DATETIMEWITHPRECISION = Table('rel_endtime_datetimewithprecision', getattr(Base, 'metadata'),
                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     index=True,
                                                     primary_key=True,
                                                     nullable=False),
                                              Column('datetimewithprecision_id',
                                                     BigIntegerType,
                                                     ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     primary_key=True,
                                                     nullable=False,
                                                     index=True)
                                              )

_REL_PRODUCEDTIME_DATETIMEWITHPRECISION = Table('rel_producedtime_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     primary_key=True,
                                                     index=True,
                                                     nullable=False),
                                              Column('datetimewithprecision_id',
                                                     BigIntegerType,
                                                     ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     primary_key=True,
                                                     nullable=False,
                                                     index=True)
                                              )

_REL_RECEIVEDTIME_DATETIMEWITHPRECISION = Table('rel_receivedtime_datetimewithprecision', getattr(Base, 'metadata'),

                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     primary_key=True,
                                                     index=True,
                                                     nullable=False),
                                              Column('datetimewithprecision_id',
                                                     BigIntegerType,
                                                     ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     primary_key=True,
                                                     nullable=False,
                                                     index=True)
                                              )

_REL_MEASURESOURCE_STRUCTUREDTEXT = Table('rel_measuresource_structuredtext', getattr(Base, 'metadata'),

                                       Column('measuresource_id',
                                              BigIntegerType,
                                              ForeignKey('measuresources.measuresource_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              primary_key=True,
                                              index=True,
                                              nullable=False),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              primary_key=True,
                                              nullable=False,
                                              index=True)
                                       )
