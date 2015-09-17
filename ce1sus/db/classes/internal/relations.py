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

_REL_EVENT_RELATED_PACKAGES = Table('rel_event_relpackage', getattr(Base, 'metadata'),

                                    Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EVENT_OBSERVABLE = Table('rel_event_observable', getattr(Base, 'metadata'),

                                    Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EVENT_INDICATOR = Table('rel_event_indicator', getattr(Base, 'metadata'),

                                    Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_REPORT_STRUCTUREDTEXT = Table('rel_report_structuredtext', getattr(Base, 'metadata'),

                                       Column('report_id',
                                              BigIntegerType,
                                              ForeignKey('reports.report_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False, primary_key=True),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              primary_key=True, index=True)
                                       )

_REL_REPORT_STRUCTUREDTEXT_SHORT = Table('rel_report_structuredtext_short', getattr(Base, 'metadata'),

                                       Column('report_id',
                                              BigIntegerType,
                                              ForeignKey('reports.report_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False, primary_key=True),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              primary_key=True, index=True)
                                       )

_REL_OBJECT_ATTRIBUTE_DEFINITION = Table(
    'objectdefinition_has_attributedefinitions', getattr(Base, 'metadata'),
    Column('oha_id', BigIntegerType, primary_key=True, nullable=False, index=True),
    Column('attributedefinition_id', BigIntegerType, ForeignKey('attributedefinitions.attributedefinition_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True),
    Column('objectdefinition_id', BigIntegerType, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
)
