from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.intended_effect import IntendedEffect
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhaseReference
from ce1sus.db.classes.cstix.common.related import RelatedExploitTarget, RelatedPackageRef, RelatedTTP
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.cstix.ttp.behavior import Behavior
from ce1sus.db.classes.cstix.ttp.resource import Resource
from ce1sus.db.classes.cstix.ttp.victim_targeting import VictimTargeting
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


_REL_TTP_HANDLING = Table('rel_ttp_handling', getattr(Base, 'metadata'),
                                Column('rth_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                )

_REL_TTP_KILLCHAINPHASE = Table('rel_ttp_killchainphase', getattr(Base, 'metadata'),
                                      Column('rik_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                      Column('killchainphasereference_id', BigIntegerType, ForeignKey('killchainphasereferences.killchainphasereference_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                      )

_REL_TTP_RELATED_PACKAGES = Table('rel_ttp_rel_package', getattr(Base, 'metadata'),
                                  Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                  Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_TTP_RELATED_TTP = Table('rel_ttp_rel_ttp', getattr(Base, 'metadata'),
                                  Column('rtt_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                  Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_TTP_RELATED_EXPLOITTARGET = Table('rel_ttp_rel_exploittarget', getattr(Base, 'metadata'),
                                  Column('rtt_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                  Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                  )

_REL_TTP_STRUCTUREDTEXT = Table('rel_ttp_structuredtext', getattr(Base, 'metadata'),
                                       Column('rtttpst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('ttp_id',
                                              BigIntegerType,
                                              ForeignKey('ttps.ttp_id',
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

_REL_TTP_STRUCTUREDTEXT_SHORT = Table('rel_ttp_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rtttpst_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('ttp_id',
                                              BigIntegerType,
                                              ForeignKey('ttps.ttp_id',
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

_REL_TTP_INTENDED_EFFECT = Table('rel_ttp_intended_effect', getattr(Base, 'metadata'),
                                      Column('rtie_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                                      Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                      )


class TTP(BaseCoreComponent, Base):

  behavior = relationship(Behavior, uselist=False, backref='ttp')
  related_ttps = relationship(RelatedTTP, secondary=_REL_TTP_RELATED_TTP, backref='ttp')
  
  intended_effects = relationship(IntendedEffect, secondary=_REL_TTP_INTENDED_EFFECT, backref='ttp')
  resources = relationship(Resource, uselist=False, backref='ttp')
  victim_targeting = relationship(VictimTargeting, uselist=False, backref='ttp')
  exploit_targets = relationship(RelatedExploitTarget, secondary=_REL_TTP_RELATED_EXPLOITTARGET, backref='ttp')
  handling = relationship(MarkingSpecification, secondary=_REL_TTP_HANDLING, backref='ttp')


  kill_chain_phases = relationship(KillChainPhaseReference, secondary=_REL_TTP_KILLCHAINPHASE, uselist=False, backref='ttp')
  # killchains = relationship('Killchain', secondary='rel_ttp_killchain')

  related_packages = relationship(RelatedPackageRef, secondary=_REL_TTP_RELATED_PACKAGES, backref='ttp')



  # custom ones related to ce1sus internals
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @property
  def parent(self):
    if self.related_ttp:
      return self.related_ttp
    elif self.event:
      return self.event
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):

    result = {
              'behavior': self.attribute_to_dict(self.behavior, cache_object),
              'related_ttps': self.attributelist_to_dict(self.ttps, cache_object),
              'indented_effects': self.attributelist_to_dict(self.intended_effects, cache_object),
              'resources': self.attribute_to_dict(self.resources, cache_object),
              'victim_targeting': self.attribute_to_dict(self.victim_targeting, cache_object),
              'exploit_targets': self.attributelist_to_dict(self.exploit_targets, cache_object),
              'kill_chain_phases': self.attribute_to_dict(self.kill_chain_phases, cache_object),
              'related_packages': self.attributelist_to_dict(self.related_packages, cache_object),
              }

    parent_dict = BaseCoreComponent.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
