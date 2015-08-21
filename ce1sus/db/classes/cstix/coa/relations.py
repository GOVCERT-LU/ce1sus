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


_REL_COA_RELATED_PACKAGESREF = Table('rel_coa_relpackage', getattr(Base, 'metadata'),
                                     Column('rcrp_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                     Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                     Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                     )

_REL_COA_IMPACT_STATEMENT = Table('rel_coa_impact_statement', getattr(Base, 'metadata'),
                                  Column('rcrp_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                  Column('statement_id', BigIntegerType, ForeignKey('statements.statement_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_COA_COST_STATEMENT = Table('rel_coa_cost_statement', getattr(Base, 'metadata'),
                                Column('rcis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                Column('statement_id', BigIntegerType, ForeignKey('statements.statement_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                )

_REL_EFFICACY_STATEMENT = Table('rel_coa_efficacy_statement', getattr(Base, 'metadata'),
                                Column('rces_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                Column('statement_id', BigIntegerType, ForeignKey('statements.statement_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                )

_REL_COA_RELCOA = Table('rel_coa_relcoa', getattr(Base, 'metadata'),
                        Column('rcrc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                        Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                        Column('relatedcoa_id', BigIntegerType, ForeignKey('relatedcoas.relatedcoa_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                        )


_REL_OBJECTIVE_STRUCTUREDTEXT = Table('rel_objective_structuredtext', getattr(Base, 'metadata'),
                                      Column('ros_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('objective_id',
                                             BigIntegerType,
                                             ForeignKey('objectives.objective_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                             index=True,
                                             nullable=False),
                                      Column('structuredtext_id',
                                             BigIntegerType,
                                                     ForeignKey('structuredtexts.structuredtext_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                             index=True,
                                             nullable=False)
                                      )

_REL_OBJECTIVE_SHORT_STRUCTUREDTEXT = Table('rel_objective_short_structuredtext', getattr(Base, 'metadata'),
                                            Column('ross_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('objective_id',
                                                   BigIntegerType,
                                                   ForeignKey('objectives.objective_id',
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

_REL_OBJECTIVE_CONFIDENCE = Table('rel_objective_confidence', getattr(Base, 'metadata'),
                                  Column('rss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('objective_id',
                                         BigIntegerType,
                                         ForeignKey('objectives.objective_id',
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
                                         index=True)
                                  )
