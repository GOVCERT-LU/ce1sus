# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 26, 2015
"""


from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.related import RelatedIdentity
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_IDENTITY_RELATED_IDENTITY = Table('rel_identity_rel_identity', getattr(Base, 'metadata'),
                                       Column('rir_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                                       Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                                       )


class Identity(Entity, Base):
  """NOTE this is not used to represent information provides etc only for internal representations"""

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['information_source',
              'resource',
              'victim_targeting',
              'threat_actor',
              'incident',
              'related_identity']

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  idref = Column('idref', UnicodeType(45), nullable=True, index=True)
  name = Column('name', UnicodeType(255), index=True, nullable=True)
  related_identities = relationship(RelatedIdentity, secondary=_REL_IDENTITY_RELATED_IDENTITY, backref='identity')

  def to_dict(self, cache_object):

    result = {
              'id_': self.convert_value(self.id_),
              'idref': self.convert_value(self.idref),
              'name': self.convert_value(self.name),
              'related_identities': self.attributelist_to_dict(self.related_identities, cache_object)
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
