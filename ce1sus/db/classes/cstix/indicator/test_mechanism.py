# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.cstix.indicator.relations import _REL_TESTMECHANISM_STATEMENT, _REL_TESTMECHANISM_INFORMATIONSOURCE
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BaseTestMechanism(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:package-{1}'.format(self.namespace, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)
  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')

  efficacy = relationship(Statement, secondary=_REL_TESTMECHANISM_STATEMENT, uselist=False)
  producer = relationship('InformationSource', secondary=_REL_TESTMECHANISM_INFORMATIONSOURCE, uselist=False)

  indicator_id = Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  indicator = relationship('Indicator', uselist=False)
  _PARENTS = ['indicator']

  type = Column(UnicodeType(20), nullable=False)
  __mapper_args__ = {
      'polymorphic_on': type,
      'polymorphic_identity': 'basetestmechanisms',
      'with_polymorphic':'*'
  }

  def to_dict(self, cache_object):

    result = {
              'id_': self.convert_value(self.id_),
              'idref': self.convert_value(self.idref),
              'efficacy': self.attribute_to_dict(self.efficacy, cache_object),
              'producer': self.attribute_to_dict(self.producer, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
