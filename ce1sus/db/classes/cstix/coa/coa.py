# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.coa.objective import Objective
from ce1sus.db.classes.cstix.common.related import RelatedPackageRef, RelatedCOA
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.cstix.common.vocabs import COAStage, CourseOfActionType
from ce1sus.db.classes.internal.core import BigIntegerType
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

class CourseOfAction(Entity, Base):
  stage_id = Column('stage_id', Integer)
  type_id = Column('type_id', Integer)

  __stage = None

  @property
  def stage(self):
    if not self.__stage:
      if self.stage_id:
        self.__stage = COAStage(self, 'stage_id')
      else:
        return None
    return self.__stage.name

  @stage.setter
  def stage(self, value):
    if not self.stage:
      self.__stage = COAStage(self, 'stage_id')
    self.stage.name = value

  __type = None

  @property
  def type(self):
    if not self.__type:
      if self.type_id:
        self.__type = CourseOfActionType(self, 'type_id')
      else:
        return None
    return self.__type.name

  @type.setter
  def type(self, value):
    if not self.type:
      self.__type = CourseOfActionType(self, 'type_id')
    self.type.name = value

  objective = relationship(Objective, backref='coa')
  # TODO: parameter_observables
  # parameter_observables = -> relationship observables
  #TODO: structured_coa = None
  
  impact = relationship(Statement, secondary=_REL_COA_IMPACT_STATEMENT, backref='coa_impact')
  cost = relationship(Statement, secondary=_REL_COA_COST_STATEMENT, backref='coa_cost')
  efficacy = relationship(Statement, secondary=_REL_EFFICACY_STATEMENT, backref='coa_efficacy')

  related_coas = relationship(RelatedCOA, secondary=_REL_COA_RELCOA, backref='coa')
  related_packages = relationship(RelatedPackageRef, secondary=_REL_COA_RELATED_PACKAGESREF, backref='coa')

  @property
  def parent(self):
    if self.coa_take:
      return self.coa_taken
    elif self.related_coa:
      return self.related_coa
    elif self.coa_requested:
      return self.coa_requested
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):
    result = {
              'stage': self.attribute_to_dict(self.stage, cache_object),
              'type': self.attribute_to_dict(self.type, cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
