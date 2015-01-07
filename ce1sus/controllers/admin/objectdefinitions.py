# -*- coding: utf-8 -*-

"""
module handing the object pages

Created: Aug 26, 2013
"""

from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException, SpecialControllerException
from ce1sus.db.classes.definitions import ObjectDefinition
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

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)

  def get_all_object_definitions(self):
    try:
      return self.obj_def_broker.get_all(ObjectDefinition.name.asc())
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
      return self.obj_def_broker.get_definition_by_chksum(chksum)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_object_definition(self, obj, user):
    try:
      obj.chksum = gen_obj_chksum(obj)
      user = self.user_broker.get_by_id(user.identifier)
      self.set_simple_logging(obj, user, insert=True)
      self.obj_def_broker.insert(obj)
      return obj
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(obj)
      raise ControllerException(u'Could not insert object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def update_object_definition(self, obj, user):
    try:
      obj.chksum = gen_obj_chksum(obj)
      user = self.user_broker.get_by_id(user.identifier)
      self.set_simple_logging(obj, user, insert=False)
      self.obj_def_broker.update(obj)
      return obj
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(obj)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_definition_by_id(self, uuid):
    try:
      self.obj_def_broker.remove_by_id(uuid)
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this object. The object is still referenced.')
    except BrokerException as error:
      raise ControllerException(error)
