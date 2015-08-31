from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.intended_effect import IntendedEffect
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhaseReference
from ce1sus.db.classes.cstix.common.related import RelatedExploitTarget, RelatedPackageRef, RelatedTTP
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.cstix.ttp.behavior import Behavior
from ce1sus.db.classes.cstix.ttp.relations import _REL_TTP_RELATED_TTP, _REL_TTP_INTENDED_EFFECT, _REL_TTP_RELATED_EXPLOITTARGET, _REL_TTP_HANDLING, \
  _REL_TTP_KILLCHAINPHASE, _REL_TTP_RELATED_PACKAGES
from ce1sus.db.classes.cstix.ttp.resource import Resource
from ce1sus.db.classes.cstix.ttp.victim_targeting import VictimTargeting
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


class TTP(BaseCoreComponent, Base):

  behavior = relationship(Behavior, uselist=False)
  related_ttps = relationship(RelatedTTP, secondary=_REL_TTP_RELATED_TTP)
  
  intended_effects = relationship(IntendedEffect, secondary=_REL_TTP_INTENDED_EFFECT)
  resources = relationship(Resource, uselist=False)
  victim_targeting = relationship(VictimTargeting, uselist=False)
  exploit_targets = relationship(RelatedExploitTarget, secondary=_REL_TTP_RELATED_EXPLOITTARGET)
  handling = relationship(MarkingSpecification, secondary=_REL_TTP_HANDLING)


  kill_chain_phases = relationship(KillChainPhaseReference, secondary=_REL_TTP_KILLCHAINPHASE, uselist=False)
  # killchains = relationship('Killchain', secondary='rel_ttp_killchain')

  related_packages = relationship(RelatedPackageRef, secondary=_REL_TTP_RELATED_PACKAGES)



  # custom ones related to ce1sus internals
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['related_ttp', 'event']
  related_ttp = relationship('RelatedTTP', uselist=False, primaryjoin='RelatedTTP.child_id==TTP.identifier')
  event = relationship('Event', uselist=False)

  def to_dict(self, cache_object):

    result = {
              'behavior': self.attribute_to_dict(self.behavior, cache_object),
              'related_ttps': self.attributelist_to_dict('related_ttps', cache_object),
              'indented_effects': self.attributelist_to_dict('intended_effects', cache_object),
              'resources': self.attribute_to_dict(self.resources, cache_object),
              'victim_targeting': self.attribute_to_dict(self.victim_targeting, cache_object),
              'exploit_targets': self.attributelist_to_dict('exploit_targets', cache_object),
              'kill_chain_phases': self.attribute_to_dict(self.kill_chain_phases, cache_object),
              'related_packages': self.attributelist_to_dict('related_packages', cache_object),
              }

    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
