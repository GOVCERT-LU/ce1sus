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
