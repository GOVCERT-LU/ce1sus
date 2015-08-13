# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.tools import ToolInformation
from ce1sus.db.classes.cstix.common.vocabs import InformationSourceRole as VocabInformationSourceRole
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_INFORMATIONSOURCE_IDENTITY = Table('rel_informationsource_identity', getattr(Base, 'metadata'),
                                  Column('rti_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('informationsource_id',
                                         BigIntegerType,
                                         ForeignKey('informationsources.informationsource_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         index=True),
                                  Column('identity_id',
                                         BigIntegerType,
                                         ForeignKey('identitys.identity_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         index=True)
                                  )

_REL_INFORMATIONSOURCE_TOOL = Table('rel_informationsource_tool', getattr(Base, 'metadata'),
                                    Column('rtt_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('informationsource_id',
                                           BigIntegerType,
                                           ForeignKey('informationsources.informationsource_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           nullable=False,
                                           index=True),
                                    Column('toolinformation_id',
                                           BigIntegerType,
                                           ForeignKey('toolinformations.toolinformation_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )

_REL_INFORMATIONSOURCE_INFORMATIONSOURCE = Table('rel_informationsource_contributing_sources', getattr(Base, 'metadata'),
                                  Column('rti_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('parent_id',
                                         BigIntegerType,
                                         ForeignKey('informationsources.informationsource_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         index=True),
                                  Column('child_id',
                                         BigIntegerType,
                                         ForeignKey('informationsources.informationsource_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         index=True)
                                  )

_REL_INFORMATIONSOURCE_STRUCTUREDTEXT = Table('rel_informationsource_structuredtext', getattr(Base, 'metadata'),
                                              Column('ras_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('informationsource_id',
                                                     BigIntegerType,
                                                     ForeignKey('informationsources.informationsource_id',
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

_REL_INFORMATIONSOURCE_TIME = Table('rel_informationsource_cyboxtime', getattr(Base, 'metadata'),
                                              Column('ras_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('informationsource_id',
                                                     BigIntegerType,
                                                     ForeignKey('informationsources.informationsource_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     index=True,
                                                     nullable=False),
                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                                     nullable=False,
                                                     index=True)
                                              )

class InformationSourceRole(Entity, Base):
  
  role_id = Column('role_id', Integer, default=None, nullable=False)
  informationsource_id = Column(BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  __role = None
  @property
  def role(self):
    if not self.__role:
      if self.role_id:
        self.__role = VocabInformationSourceRole(self, 'role_id')
    return self.__role.name

  @role.setter
  def role(self, role):
    if not self.__role:
      self.__role = VocabInformationSourceRole(self, 'role_id')
    self.__role.name = role


  def to_dict(self, cache_object):
    result = {'name': self.convert_value(self.role)}
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class InformationSource(Entity, Base):
  """ An information source is a bit tricky as the groups contain half of the needed elements """

  description = relationship(StructuredText, secondary=_REL_INFORMATIONSOURCE_STRUCTUREDTEXT, uselist=False)
  identity = relationship('Identity', secondary=_REL_INFORMATIONSOURCE_IDENTITY, uselist=False)

  contributing_sources = relationship('InformationSource',
                                      secondary=_REL_INFORMATIONSOURCE_INFORMATIONSOURCE,
                                      primaryjoin='InformationSource.identifier == rel_informationsource_contributing_sources.c.parent_id',
                                      secondaryjoin='InformationSource.identifier == rel_informationsource_contributing_sources.c.child_id',)
  
  time = relationship(CyboxTime, secondary=_REL_INFORMATIONSOURCE_TIME, uselist=False)
  tools = relationship(ToolInformation, secondary=_REL_INFORMATIONSOURCE_TOOL)
  roles = relationship(InformationSourceRole)
  # TODO: references -> relation

  def to_dict(self, cache_object):
    copy = cache_object.make_copy()
    copy.inflated = True
    if cache_object.complete:
      result = {
                'description':self.attribute_to_dict(self.description, cache_object),
                'identity': self.attribute_to_dict(self.identity, copy),
                'time': self.attribute_to_dict(self.time, cache_object),
                'tools': self.attributelist_to_dict(self.tools, cache_object),
                'roles': self.attributelist_to_dict(self.roles, copy),
                'contributing_sources': self.attributelist_to_dict(self.contributing_sources, copy)
              }
    else:
      result = {
                'identity': self.attribute_to_dict(self.identity, cache_object),
                'time': self.attribute_to_dict(self.identity, cache_object),
                'roles': self.attributelist_to_dict(self.roles, cache_object),
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
