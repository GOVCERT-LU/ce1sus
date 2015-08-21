# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.coa.objective import Objective
from ce1sus.db.classes.cstix.coa.relations import _REL_COA_IMPACT_STATEMENT, _REL_COA_COST_STATEMENT, _REL_EFFICACY_STATEMENT, _REL_COA_RELCOA, \
  _REL_COA_RELATED_PACKAGESREF
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.cstix.common.vocabs import COAStage, CourseOfActionType
from ce1sus.db.classes.cstix.incident.relations import _REL_COATAKEN_COA, _REL_COAREQUESTED_COA
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


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

  objective = relationship(Objective)
  # TODO: parameter_observables
  # parameter_observables = -> relationship observables
  #TODO: structured_coa = None
  
  impact = relationship(Statement, secondary=_REL_COA_IMPACT_STATEMENT)
  cost = relationship(Statement, secondary=_REL_COA_COST_STATEMENT)
  efficacy = relationship(Statement, secondary=_REL_EFFICACY_STATEMENT)

  related_coas = relationship('RelatedCOA', secondary=_REL_COA_RELCOA)
  related_packages = relationship('RelatedPackageRef', secondary=_REL_COA_RELATED_PACKAGESREF)

  _PARENTS = ['coa_taken', 'related_coa', 'coa_requested']
  related_coa = relationship('RelatedCOA', uselist=False, primaryjoin='RelatedCOA.child_id==CourseOfAction.identifier')
  coa_taken = relationship('COATaken', uselist=False, secondary=_REL_COATAKEN_COA)
  coa_requested = relationship('COARequested', uselist=False, secondary=_REL_COAREQUESTED_COA)

  def to_dict(self, cache_object):
    result = {
              'stage': self.attribute_to_dict(self.stage, cache_object),
              'type': self.attribute_to_dict(self.type, cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
