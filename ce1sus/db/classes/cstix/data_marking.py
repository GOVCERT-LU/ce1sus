# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.relations import _REL_CAMPAIGN_HANDLING
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.core.relations import _REL_STIXHEADER_HANDLING
from ce1sus.db.classes.cstix.exploit_target.relations import _REL_EXPLOITTARGET_HANDLING
from ce1sus.db.classes.cstix.incident.relations import _REL_INCIDENT_HANDLING
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICATOR_HANDLING
from ce1sus.db.classes.cstix.relations import _REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base
from ce1sus.helpers.version import Version
from ce1sus.db.classes.cstix.threat_actor.relations import _REL_THREATACTOR_HANDLING
from ce1sus.db.classes.cstix.ttp.relations import _REL_TTP_HANDLING


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MarkingStructure(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['markingspecification']
  markingspecification = relationship('MarkingSpecification', uselist=False)

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')

  marking_model_name = Column('marking_model_name', UnicodeTextType())
  marking_model_ref = Column('marking_model_ref', UnicodeTextType())

  # celsus_specific
  markingspecification_id = Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  type = Column(UnicodeType(20), nullable=False)

  __mapper_args__ = {
      'polymorphic_on': type,
      'polymorphic_identity': 'markingstructures',
      'with_polymorphic':'*'
  }

  def to_dict(self, cache_object):

    result = {
              'id_': self.convert_value(self.id_),
              'marking_model_name': self.convert_value(self.marking_model_name),
              'marking_model_ref': self.convert_value(self.marking_model_ref),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class MarkingSpecification(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)



  _PARENTS = ['campaign',
              'stix_header',
              'exploit_target',
              'ttp',
              'indicator',
              'threat_actor',
              'incident']

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_HANDLING, uselist=False)
  stix_header = relationship('STIXHeader', secondary=_REL_STIXHEADER_HANDLING, uselist=False)
  exploit_target = relationship('ExploitTarget', uselist=False, secondary=_REL_EXPLOITTARGET_HANDLING)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_HANDLING)
  incident = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_HANDLING)
  threat_actor = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_HANDLING)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_HANDLING)

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  version_db = Column('version', UnicodeType(40), nullable=True)
  controlled_structure = Column('controlled_structure', UnicodeType(255))
  marking_structures = relationship(MarkingStructure)
  information_source = relationship(InformationSource, secondary=_REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE, uselist=False)



  __version = None
  @property
  def version(self):
    if self.__version is None:
      self.__version = Version(self.version_db, self)
    return self.__version
  @version.setter
  def version(self, value):
    if self.__version is None:
      self.__version = Version(self.version_db, self)
    self.__version.version = value

  def to_dict(self, cache_object):

    result = {
              'id_': self.convert_value(self.id_),
              'version': self.convert_value(self.version_db),
              'controlled_structure': self.convert_value(self.controlled_structure),
              'marking_structures': self.attributelist_to_dict('marking_structures', cache_object),
              'information_source': self.attribute_to_dict(self.information_source, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
