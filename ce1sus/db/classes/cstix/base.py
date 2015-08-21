# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 31, 2015
"""
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.common.checks import is_object_viewable
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import BaseElement
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BaseCoreComponent(Entity):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')

  @declared_attr
  def idref(self):
    return Column(u'{0}_idref'.format(self.get_classname().lower()), UnicodeType(255), nullable=True, index=True)

  title = Column('title', UnicodeType(255), index=True, nullable=True)

  @declared_attr
  def description(self):
    return relationship('StructuredText', secondary='rel_{0}_structuredtext'.format(self.get_classname().lower()), uselist=False)

  @declared_attr
  def short_description(self):
    return relationship('StructuredText', secondary='rel_{0}_structuredtext_short'.format(self.get_classname().lower()), uselist=False)

  version_db = Column('version', UnicodeType(40), default=u'0.0.0', nullable=False)

  @property
  def information_source(self):
    return relationship('InformationSource', secondary='rel_{0}_informationssource'.format(self.get_classname().lower()), uselist=False)

  timestamp = Column(DateTime)

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

  # ce1sus specific
  def get_description_for_permissions(self, event_permissions, user):
    return self.description

  def get_short_description_for_permissions(self, event_permissions, user):
    return self.short_description

  def to_dict(self, cache_object):
    description = None
    short_description = None
    information_source = None
    if cache_object.inflated:
      if is_object_viewable(self.description, cache_object):
        description = self.description.to_dict(cache_object)
      if is_object_viewable(self.short_description, cache_object):
        short_description = self.short_description.to_dict(cache_object)
      if is_object_viewable(self.information_source, cache_object):
        information_source = self.information_source.to_dict(cache_object)
    if cache_object.complete:
      result = {'id_':self.convert_value(self.id_),
                'idref':self.convert_value(self.idref),
                'description': description,
                'short_description':short_description,
                'information_source':information_source,
                'version': self.convert_value(self.version_db)
                }
    else:
      result = {'id_':self.convert_value(self.id_),
                'idref':self.convert_value(self.idref),
                'version': self.convert_value(self.version_db)
                }
    # merge parent
    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
