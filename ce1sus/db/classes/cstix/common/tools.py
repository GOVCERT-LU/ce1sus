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
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_TOOLINFORMATION_STRUCTUREDTEXT = Table('rel_toolinformation_structuredtext', getattr(Base, 'metadata'),
                                              Column('ras_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('toolinformation_id',
                                                     BigIntegerType,
                                                     ForeignKey('toolinformations.toolinformation_id',
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
                                                     index=True))

_REL_TOOLINFORMATION_STRUCTUREDTEXT_SHORT = Table('rel_toolinformation_structuredtextshort', getattr(Base, 'metadata'),
                                              Column('ras_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('toolinformation_id',
                                                     BigIntegerType,
                                                     ForeignKey('toolinformations.toolinformation_id',
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
                                                     index=True))

class ToolInformation(Entity, Base):
  
  """ Note to many unknowns here setting up basics """

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['information_source', 'resource']


  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')

  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)
  name = Column('name', UnicodeType(255), index=True, nullable=False)
  # TODO: Tool type 0..n
  description = relationship(StructuredText, secondary=_REL_TOOLINFORMATION_STRUCTUREDTEXT, uselist=False, backref='tool_information_description')
  # TODO: references ToolReference 0..n
  vendor = Column('vendor', UnicodeType(255), index=True, nullable=False)
  version_db = Column('version', UnicodeType(40), nullable=True)
  service_pack = Column('service_pack', UnicodeType(255), index=True, nullable=False)
  # TODO: Tool_Specific_Data 0..1
  # TODO: Tool hashes 0..n
  # TODO: Tool configuration 0..1
  # TODO: Execution_Environment 0..1
  # TODO: errors
  # TODO: metadata
  # TODO: compensation_model
  title = Column('title', UnicodeType(255), index=True, nullable=False)
  short_description = relationship(StructuredText, secondary=_REL_TOOLINFORMATION_STRUCTUREDTEXT_SHORT, uselist=False, backref='tool_information_short_description')

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
    if cache_object.complete:
      result = {'id_': self.convert_value(self.id_),
                'idref': self.convert_value(self.idref),
                'name': self.convert_value(self.name),
                'description': self.attribute_to_dict(self.description, cache_object),
                'vendor': self.convert_value(self.vendor),
                'version': self.convert_value(self.version_db),
                'service_pack': self.convert_value(self.service_pack),
                'title': self.convert_value(self.title),
                'short_description': self.attribute_to_dict(self.short_description, cache_object),
                }
    else:
      result = {'id_': self.convert_value(self.id_),
                'idref': self.convert_value(self.idref),
                'name': self.convert_value(self.name),
                'vendor': self.convert_value(self.vendor),
                'version': self.convert_value(self.version_db),
                'service_pack': self.convert_value(self.service_pack),
                'title': self.convert_value(self.title),
                }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
