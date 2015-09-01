# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from ce1sus.helpers.bitdecoder import BitBase
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.common import TLP
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_MAINGROUP_GROUPS = Table('group_has_groups', getattr(Base, 'metadata'),
                              Column('ghg_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                              Column('group_id', BigIntegerType, ForeignKey('groups.group_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True),
                              Column('rel_group_id', BigIntegerType, ForeignKey('groups.group_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True))


class GroupRights(BitBase):
  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can set group via rest inserts
  """

  DOWNLOAD = 0
  TLP_PROPAGATION = 1
  SYSTEM_OWNER = 2

  @property
  def can_download(self):
    return self._get_value(GroupRights.DOWNLOAD)

  @can_download.setter
  def can_download(self, value):
    self._set_value(GroupRights.DOWNLOAD, value)

  @property
  def propagate_tlp(self):
    return self._get_value(GroupRights.TLP_PROPAGATION)

  @propagate_tlp.setter
  def propagate_tlp(self, value):
    self._set_value(GroupRights.TLP_PROPAGATION, value)

  @property
  def system_group(self):
    return self._get_value(GroupRights.SYSTEM_OWNER)

  @system_group.setter
  def system_group(self, value):
    self._set_value(GroupRights.SYSTEM_OWNER, value)

  def to_dict(self, cache_object):
    return {'downloadfiles': self.can_download,
            'propagate_tlp': self.propagate_tlp}

class EventPermissions(BitBase):

  ADD = 0
  MODIFY = 1
  DELETE = 2
  VALIDATE = 3
  PROPOSE = 4
  SET_GROUPS = 5
  VIEW_SHARE = 6

  @property
  def can_view(self):
    return True

  @property
  def can_view_non_shared(self):
    # TODO: implement non shared to see
    # Note this is for non shared elements
    return self._get_value(EventPermissions.VIEW_SHARE)

  @can_view_non_shared.setter
  def can_view_non_shared(self, value):
    # Note this is for non shared elements
    self._set_value(EventPermissions.VIEW_SHARE, value)

  @property
  def can_propose(self):
    # Not used anymore
    return self._get_value(EventPermissions.PROPOSE)

  @can_propose.setter
  def can_propose(self, value):
    # Not used anymore
    self._set_value(EventPermissions.PROPOSE, value)

  @property
  def can_add(self):
    return self._get_value(EventPermissions.ADD)

  @can_add.setter
  def can_add(self, value):
    # if you can add you can see
    self._set_value(EventPermissions.ADD, value)

  @property
  def can_modify(self):
    return self._get_value(EventPermissions.MODIFY)

  @can_modify.setter
  def can_modify(self, value):
    # if you can modify you can see
    self._set_value(EventPermissions.MODIFY, value)

  @property
  def can_delete(self):
    return self._get_value(EventPermissions.DELETE)

  @can_delete.setter
  def can_delete(self, value):
    # if you can delete you can see
    self._set_value(EventPermissions.DELETE, value)

  @property
  def can_validate(self):
    return self._get_value(EventPermissions.VALIDATE)

  @can_validate.setter
  def can_validate(self, value):
    # if you can validate you can see
    self._set_value(EventPermissions.VALIDATE, value)

  @property
  def set_groups(self):
    return self._get_value(EventPermissions.SET_GROUPS)

  @set_groups.setter
  def set_groups(self, value):
    # if you can validate you can see
    self._set_value(EventPermissions.SET_GROUPS, value)

  def set_all(self):
    self.can_add = True
    self.can_modify = True
    self.can_delete = True
    self.can_propose = True
    self.can_validate = True
    self.set_groups = True

  def set_default(self):
    # Set no default values
    pass

  def to_dict(self, cache_object):
    return {'add': self.can_add,
            'modify': self.can_modify,
            'validate': self.can_validate,
            'delete': self.can_delete,
            'set_groups': self.set_groups
            }

class Group(BaseObject, Base):
  name = Column('name', UnicodeType(255), nullable=False, unique=True)
  description = Column('description', UnicodeTextType())
  tlp_lvl = Column('tlplvl', Integer, default=3, nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None
  __default_bit_code = None
  default_dbcode = Column('default_code', Integer, default=0, nullable=False)
  email = Column('email', UnicodeType(255), unique=True)
  gpg_key = Column('gpg_key', UnicodeTextType())
  send_usermails = Column('usermails', Boolean, default=False)
  children = relationship('Group',
                          secondary=_REL_MAINGROUP_GROUPS,
                          primaryjoin='Group.identifier == group_has_groups.c.group_id',
                          secondaryjoin='Group.identifier == group_has_groups.c.rel_group_id',
                          order_by='Group.name',
                          lazy='joined'
                          )
  notifications = Column('notifications', Boolean, default=False, nullable=False)

  def equals(self, group):
    if self.uuid == group.uuid:
      return True
    else:
      if self.name == group.name:
        return True
      else:
        return False

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """

    return TLP.get_by_id(self.tlp_lvl)

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.tlp_lvl = TLP.get_by_value(text)

  @property
  def default_permissions(self):
    if self.__default_bit_code is None:
      if self.default_dbcode is None:
        self.__default_bit_code = EventPermissions('0', self, 'default_dbcode')
      else:
        self.__default_bit_code = EventPermissions(self.default_dbcode, self, 'default_dbcode')
    return self.__default_bit_code

  @property
  def permissions(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = GroupRights('0', self)
      else:
        self.__bit_code = GroupRights(self.dbcode, self)
    return self.__bit_code

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Verify validation of Group Object
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True,
                                  minLength=3)
    # TODO: validate
    return ObjectValidator.isObjectValid(self)


  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
              'name': self.convert_value(self.name),
              'description': self.convert_value(self.description),
              'permissions': self.attribute_to_dict(self.permissions, cache_object),
              'default_event_permissions': self.attribute_to_dict(self.default_permissions, cache_object),
              'email': self.convert_value(self.email),
              'gpg_key': self.convert_value(self.gpg_key),
              'tlp_lvl': self.convert_value(self.tlp_lvl),
              'tlp': self.convert_value(self.tlp),
              'children': self.attributelist_to_dict('children', cache_object),
              'notifications': self.convert_value(self.notifications)
              }
    else:
      result = {
              'name': self.name
              }

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
