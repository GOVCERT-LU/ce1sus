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

_REL_CAMPAIGN_INFORMATIONSOURCE = Table('rel_campaign_informationsource', getattr(Base, 'metadata'),
                                       Column('rcis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('campaign_id',
                                              BigIntegerType,
                                              ForeignKey('campaigns.campaign_id',
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

_REL_OBSERVABLE_COMPOSITION = Table('rel_observable_composition', getattr(Base, 'metadata'),
                                    Column('roc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('observablecomposition_id', BigIntegerType, ForeignKey('observablecompositions.observablecomposition_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                    Column('child_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
                                    )

_REL_OBSERVABLE_STRUCTUREDTEXT = Table('rel_observable_structuredtext', getattr(Base, 'metadata'),
                                       Column('rtobservablest_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('observable_id',
                                              BigIntegerType,
                                              ForeignKey('observables.observable_id',
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

_REL_OBSERVABLE_OBJECT = Table('rel_observable_object', getattr(Base, 'metadata'),
                                    Column('roo_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                    Column('object_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
                                    )
