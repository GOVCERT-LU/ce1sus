# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_MARKINGSTRUCTURE_STATEMENT = Table('rel_markingstructure_statement', getattr(Base, 'metadata'),
                                       Column('rtous_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('markingstructure_id',
                                              BigIntegerType,
                                              ForeignKey('markingstructures.markingstructure_id',
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


_REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE = Table('rel_markingspecification_informationsource', getattr(Base, 'metadata'),
                                       Column('rmsis_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('markingspecification_id',
                                              BigIntegerType,
                                              ForeignKey('markingspecifications.markingspecification_id',
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

class MarkingStructure(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['markingspecification']

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

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  version_db = Column('version', UnicodeType(40), nullable=True)
  controlled_structure = Column('controlled_structure', UnicodeType(255))
  marking_structures = relationship(MarkingStructure, backref='markingspecification')
  information_source = relationship(InformationSource, secondary=_REL_MARKINGSPECIFICATIONS_INFORMATIONSOURCE, uselist=False, backref='markingspecification')

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
              'marking_structures': self.attributelist_to_dict(self.marking_structures, cache_object),
              'information_source': self.attribute_to_dict(self.information_source, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
