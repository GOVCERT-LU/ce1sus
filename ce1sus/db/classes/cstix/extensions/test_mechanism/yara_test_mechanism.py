# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.indicator.test_mechanism import BaseTestMechanism
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class YaraTestMechanism(BaseTestMechanism):

  # override identifier to keep the polymorphics
  identifier = Column(BigIntegerType, ForeignKey('basetestmechanisms.basetestmechanism_id'), primary_key=True)

  version_db = Column('version', UnicodeType(40), default=u'1.0.0', nullable=False)
  rule = Column('rule', UnicodeTextType(), nullable=False)

  __mapper_args__ = {'polymorphic_identity':'yaratestmechanism'}

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
              'rule': self.convert_value(self.rule),
              'version': self.convert_value(self.version_db)
              }

    parent_dict = BaseTestMechanism.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
