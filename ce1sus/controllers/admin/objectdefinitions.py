# -*- coding: utf-8 -*-

"""
module handing the object pages

Created: Aug 26, 2013
"""

from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException, SpecialControllerException
from ce1sus.db.classes.internal.definitions import ObjectDefinition
from ce1sus.db.common.broker import BrokerException, NothingFoundException, IntegrityException, ValidationException
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def gen_obj_chksum(obj):
  return hashSHA1(obj.name)


class ObjectDefinitionController(BaseController):
  """Controller handling all the requests for objects"""

  def get_defintion_by_name(self, name):
    try:
      return self.obj_def_broker.get_defintion_by_name(name)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_object_definitions(self):
    try:
      return self.obj_def_broker.get_all(ObjectDefinition.name.asc())
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_definitions_by_uuid(self, uuid):
    try:
      return self.obj_def_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_definitions_by_id(self, object_id):
    try:
      return self.obj_def_broker.get_by_id(object_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_definition_by_chksum(self, chksum):
    try:
      return self.obj_def_broker.get_defintion_by_chksum(chksum)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_object_definition_by_chksums(self, chksums):
    try:
      return self.obj_def_broker.get_defintion_by_chksums(chksums)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_object_definition(self, obj, commit=True):
    try:
      self.obj_def_broker.insert(obj, False)
      self.obj_def_broker.do_commit(commit)
      return obj
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(obj)
      raise ControllerException(u'Could not insert object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def update_object_definition(self, obj, commit=True):
    if obj.cybox_std:
      raise ControllerException(u'Could not update object definition as the object is part of the cybox standard')
    try:
      self.obj_def_broker.update(obj, commit)
      return obj
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(obj)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_definition_by_id(self, identifier):
    try:
      self.obj_def_broker.remove_by_id(identifier)
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this object. The object is still referenced.')
    except BrokerException as error:
      raise ControllerException(error)

  def remove_definition_by_uuid(self, uuid):
    try:
      self.obj_def_broker.remove_by_uuid(uuid)
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this object. The object is still referenced.')
    except BrokerException as error:
      raise ControllerException(error)
