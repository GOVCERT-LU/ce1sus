# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.tools import ToolInformation
from ce1sus.db.classes.cstix.ttp.infrastructure import Infrastructure
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_RESOURCE_TOOLINFORMATION = Table('rel_resource_toolinformation', getattr(Base, 'metadata'),
                                    Column('rrti_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('resource_id',
                                           BigIntegerType,
                                           ForeignKey('resources.resource_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('toolinformation_id',
                                           BigIntegerType,
                                           ForeignKey('toolinformations.toolinformation_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )

_REL_RESOURCE_IDENTITIY = Table('rel_resource_identity', getattr(Base, 'metadata'),
                                    Column('rrti_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('resource_id',
                                           BigIntegerType,
                                           ForeignKey('resources.resource_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('identity_id',
                                           BigIntegerType,
                                           ForeignKey('identitys.identity_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )

class Resource(Entity, Base):

  tools = relationship(ToolInformation, secondary=_REL_RESOURCE_TOOLINFORMATION, backref='resource')
  infrastructure = relationship(Infrastructure, uselist=False, backref='resource')
  personas = relationship(Identity, secondary=_REL_RESOURCE_IDENTITIY, backref='resource')

  _PARENTS = ['ttp']
  ttp = relationship('TTP', uselist=False)

  # custom ones related to ce1sus internals

  ttp_id = Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  def to_dict(self, cache_object):

    result = {
              'tools': self.attributelist_to_dict(self.tools, cache_object),
              'infrastructure': self.attribute_to_dict(self.infrastructure, cache_object),
              'personas': self.attributelist_to_dict(self.personas, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
