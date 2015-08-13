# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_TESTMECHANISM_INFORMATIONSOURCE = Table('rel_basetestmechanism_informationsource', getattr(Base, 'metadata'),
                                       Column('rbtmis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
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

_REL_TESTMECHANISM_STATEMENT = Table('rel_basetestmechanism_statement', getattr(Base, 'metadata'),
                                       Column('rsmss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('statement_id',
                                             BigIntegerType,
                                             ForeignKey('statements.statement_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

_REL_TESTMECHANISM_STRUCTUREDTEXT = Table('rel_testmechanism_structuredtext', getattr(Base, 'metadata'),
                                       Column('rsmss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
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

_REL_TESTMECHANISM_VOCABSTRING = Table('rel_testmechanism_statement', getattr(Base, 'metadata'),
                                       Column('rsmss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('basetestmechanism_id',
                                              BigIntegerType,
                                              ForeignKey('basetestmechanisms.basetestmechanism_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('vocabstring_id',
                                             BigIntegerType,
                                             ForeignKey('vocabstrings.vocabstring_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              nullable=False,
                                              index=True)
                                       )

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
  producer = relationship(InformationSource, secondary=_REL_TESTMECHANISM_INFORMATIONSOURCE, uselist=False)

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
