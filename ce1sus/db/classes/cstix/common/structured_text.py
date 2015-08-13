# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column
from sqlalchemy.types import UnicodeText, Unicode, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StructuredText(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  # TODO: make structured text as Entity
  value = Column('description', UnicodeTextType(), nullable=False)
  structuring_format = Column('structuring_format', UnicodeType(10), nullable=False, default=u'text')
  ordinality = Column('ordinality', Integer, nullable=False, default=1)

  def to_dict(self, cache_object):
    result = {'id_': self.convert_value(self.id_),
              'structuring_format': self.convert_value(self.structuring_format),
              'value':self.convert_value(self.value),
              'ordinality':self.convert_value(self.ordinality)
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
