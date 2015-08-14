# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.indicator.test_mechanism import BaseTestMechanism
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeTextType, UnicodeType
from ce1sus.db.common.session import Base
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class SnortRule(Entity, Base):
  snorttestmechanism_id = Column('basetestmechanism_id', BigIntegerType, ForeignKey('basetestmechanisms.basetestmechanism_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rule = Column('rule', UnicodeTextType(), nullable=False)

  @property
  def parent(self):
    return self.snort_test_mechanism

  def to_dict(self, cache_object):

    result = {
              'rule': self.convert_value(self.rule)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class SnortTestMechanism(BaseTestMechanism):
  
  # override identifier to keep the polymorphics
  identifier = Column(BigIntegerType, ForeignKey('basetestmechanisms.basetestmechanism_id'), primary_key=True)

  product_name = None
  version_db = Column('version', UnicodeType(40), default=u'1.0.0', nullable=False)
  rules = relationship(SnortRule, backref='snort_test_mechanism')
  # TODO: event_filters
  # TODO: rate_filters
  # TODO: event_suppressions

  __mapper_args__ = {'polymorphic_identity':'snorttestmechanism'}

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
              'rules': self.attributelist_to_dict(self.rules, cache_object),
              'version': self.convert_value(self.version_db)
              }

    parent_dict = BaseTestMechanism.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
