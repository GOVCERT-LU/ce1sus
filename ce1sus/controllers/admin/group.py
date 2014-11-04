# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug 26, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.common.broker import IntegrityException, BrokerException, ValidationException, DeletionException, NothingFoundException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0904
class GroupController(BaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config):
    BaseController.__init__(self, config)

  def get_all_groups(self):
    try:
      return self.group_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_group_by_id(self, group_id):
    try:
      return self.group_broker.get_by_id(group_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_group(self, group, validate=True):
    try:
      self.group_broker.insert(group, validate=validate)

    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(group)
      raise ControllerException(u'Could not add group due to: {0}'.format(message))
    except (BrokerException) as error:
      raise ControllerException(error)

  def update_group(self, group):
    try:
      self.group_broker.update(group)
      return group
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(group)
      raise ControllerException(u'Could not update group due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_group_by_id(self, identifier):
    try:
      self.group_broker.remove_by_id(identifier)
    except IntegrityException as error:
      raise ControllerException('Cannot delete group. The group is referenced by elements. Disable this group instead.')
    except DeletionException:
      raise ControllerException('This group cannot be deleted')
    except BrokerException as error:
      raise ControllerException(error)
