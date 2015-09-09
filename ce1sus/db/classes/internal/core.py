# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""




from ce1sus.helpers.common.objects import get_fields
from datetime import datetime
from sqlalchemy.ext.declarative.api import declared_attr, DeclarativeMeta
from sqlalchemy.orm import relationship, joinedload, lazyload
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import  DateTime
from types import NoneType

from ce1sus.common import merge_dictionaries
from ce1sus.common.utils import instance_code
from ce1sus.db.classes.internal.common import TLP, Properties
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType
from ce1sus.db.classes.internal.usrmgt.user import User


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SimpleLoggingInformations(BaseObject):

  created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
  modified_on = Column(DateTime, default=datetime.utcnow(), nullable=False)
  # TODO: remove validation errors

  @declared_attr
  def creator_id(self):
    return Column('creator_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator(self):
    return relationship(User, primaryjoin='{0}.creator_id==User.identifier'.format(self.get_classname()))

  @declared_attr
  def modifier_id(self):
    return Column('modifier_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def modifier(self):
    return relationship(User, primaryjoin='{0}.modifier_id==User.identifier'.format(self.get_classname()))

  def to_dict(self, cache_object):
    cache_object_copy = cache_object.make_copy()
    cache_object_copy.inflated = False
    cache_object_copy.complete = False
    """
    if cache_object.permission_controller.is_user_priviledged(cache_object.user):
      result = {'creator_id': self.convert_value(self.creator.uuid),
                 'creator': self.creator.to_dict(cache_object_copy),
                 'modifier_id': self.convert_value(self.modifier.uuid),
                 'modifier': self.modifier.to_dict(cache_object_copy),
                 'created_at': self.convert_value(self.created_at),
                 'modified_on': self.convert_value(self.modified_on),
                }
    else:
      result = {
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on)
                }
    """
    result = {
              'created_at': self.convert_value(self.created_at),
              'modified_on': self.convert_value(self.modified_on)
              }

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(parent_dict, result)


class ExtendedLogingInformations(SimpleLoggingInformations):

  @declared_attr
  def creator_group_id(self):
    return Column('creator_group_id', BigIntegerType, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator_group(self):
    return relationship('Group', primaryjoin='{0}.creator_group_id==Group.identifier'.format(self.get_classname()))

  def to_dict(self, cache_object):
    cache_object_copy = cache_object.make_copy()
    cache_object_copy.inflated = False
    cache_object_copy.complete = False
    parent_dict = SimpleLoggingInformations.to_dict(self, cache_object)
    """
    if cache_object.permission_controller.is_user_priviledged(cache_object.user):
      child_dict = {'creator_group_id': self.convert_value(self.creator_group.uuid),
                    'creator_group': self.creator_group.to_dict(cache_object_copy),
                    }
    else:
      child_dict = {}
    """
    child_dict = {}
    return merge_dictionaries(parent_dict, child_dict)


class BaseElement(ExtendedLogingInformations):

  __bit_code = None
  __tlp_obj = None

  @property
  def tlp_level_id(self):
    return self.path.item_tlp_level_id

  @tlp_level_id.setter
  def tlp_level_id(self, value):
    self.path.item_tlp_level_id = value

  @property
  def dbcode(self):
    return self.path.item_dbcode

  @dbcode.setter
  def dbcode(self, value):
    self.path.item_dbcode = value

  @declared_attr
  def path(self):
    return relationship('Path', secondary='rel_{0}_path'.format(self.get_classname().lower()), uselist=False, lazy='joined')

  _PARENTS = list()

  def __load_pared_by_join(self):
    session = self.session
    joined_loads = list()
    for attr_name in self._PARENTS:
      if hasattr(self.__class__, attr_name):
        joined_loads.append(joinedload(attr_name))
      else:
        raise ValueError('Attribute {0} is not mapped for {1}'.format(attr_name, self.get_classname()))
    if joined_loads is None:
      if self.get_classname() != 'Event':
        raise ValueError('Parent for {0} {1} cannot be found'.format(self.get_classname(), self.uuid))
      else:
        return None
    else:
      instance = session.query(self.__class__).options(*joined_loads).filter(self.__class__.identifier == self.identifier).one()
      for attr_name in self._PARENTS:
        item = getattr(instance, attr_name)
        if item:
          return item

  @property
  def parent(self):
    if self.path and self.path.path:
      parent_table = self.path.parent_table
      for attr_name in self._PARENTS:
        table_name = getattr(self.__class__, attr_name).property.mapper.mapped_table.name
        if table_name == parent_table:
          return getattr(self, attr_name)

    else:
      for attr_name in self._PARENTS:
        if hasattr(self.__class__, attr_name):
          item = getattr(self, attr_name)
          if item:
            return item
        else:
          raise ValueError('Attribute {0} is not mapped for {1}'.format(attr_name, self.get_classname()))

    if self.get_classname() != 'Event':
      raise ValueError('Parent for {0} {1} cannot be found'.format(self.get_classname(), self.uuid))
    else:
      return None
  @parent.setter
  def parent(self, instance):
    # TODO: verify if this is feasible for long term (note as there can be more parents)
    instance_classname = instance.get_classname()
    parent_set = False
    for attr_name in self._PARENTS:
      if hasattr(self, attr_name):
        attribute_class_name = getattr(self.__class__, attr_name).mapper.class_.get_classname()
        if instance_classname == attribute_class_name:
          setattr(self, attr_name, instance)
          parent_set = True
          break
    if not parent_set:
      raise ValueError('Cannot set instance of class {0} as parent for it in class {1}'.format(instance_classname, self.get_classname()))

  def delink_parent(self):
    for attr_name in self._PARENTS:
      if hasattr(self, attr_name):
        item = getattr(self, attr_name)
        if isinstance(item, BaseElement) or isinstance(item, NoneType):
          setattr(self, attr_name, None)
        else:
          setattr(self, attr_name, list())

  @property
  def root(self):
    if self.path:
      return self.path.root
    else:
      return None

  def set_id(self, id_):
    namespace, uuid = self.parse_id(id_)
    if namespace and not self.namespace:
      self.namespace = namespace
    if uuid and not self.uuid:
      self.uuid = uuid

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code

  @properties.setter
  def properties(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """

    return TLP.get_by_id(self.tlp_level_id)

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.tlp_level_id = TLP.get_by_value(text)
    
  def to_dict(self, cache_object):
    result = {'tlp': self.convert_value(self.tlp),
              'properties': self.properties.to_dict(),
              }
    parent_dict = ExtendedLogingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def attribute_to_dict(self, attribute, cache_object):
    if attribute and not isinstance(attribute, RelationshipProperty):
      # TODO: Check attribute type
      if isinstance(attribute, BaseElement):
        if cache_object.permission_controller.is_instance_viewable(attribute, cache_object):
          return attribute.to_dict(cache_object)
      else:
        return attribute.to_dict(cache_object)

  def attributelist_to_dict(self, attribute, cache_object):
    result = list()
    if cache_object.inflated:
      attribute = getattr(self, attribute)
      if attribute:
        for item in attribute:
          if cache_object.permission_controller.is_instance_viewable(item, cache_object):
            result.append(self.attribute_to_dict(item, cache_object))
      return result
    return None
