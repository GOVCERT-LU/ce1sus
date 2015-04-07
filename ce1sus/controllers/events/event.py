# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.common.checks import is_event_owner
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.event.comments import CommentBroker
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.classes.event import EventGroupPermission
from ce1sus.db.classes.group import EventPermissions
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException, NothingFoundException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from ce1sus.db.brokers.event.reportbroker import ReferenceBroker


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def get_all_attributes_from_event(event):
  attributes = list()
  for obj in event.objects:
    __get_all_attributes_from_obj(attributes, obj)
  return attributes


def __get_all_attributes_from_obj(attributes, obj):
  attributes += obj.attributes
  for child in obj.children:
    __get_all_attributes_from_obj(attributes, child)


class EventController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.event_broker = self.broker_factory(EventBroker)
    self.comment_broker = self.broker_factory(CommentBroker)
    self.reference_broker = self.broker_factory(ReferenceBroker)

  def get_all_misp_events(self):
    try:
      references_with_misp = self.reference_broker.get_all_misp_references()
      events_ids = dict()
      for reference in references_with_misp:
        splitted = reference.value.split()
        event_id = splitted[-1]
        report = reference.report
        events_ids[report.event_id] = event_id

      events = self.event_broker.get_all_by_ids(events_ids.keys())

      return (events, events_ids)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_event(self, user, event, mkrelations=True, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    self.logger.debug('User {0} inserts a new event'.format(user.username))
    try:
      # the the creator

      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event, user, user.group, True)
      if commit:
        # do this only if there is a commit
        # set the own user group to the groups of the event and fill permissions
        permissions = self.get_event_user_permissions(event, user)
        group = self.group_broker.get_by_id(user.group.identifier)

        event_permission = EventGroupPermission()
        event_permission.permissions = permissions
        event_permission.group = group
        self.set_extended_logging(event_permission, user, user.group, True)

        event.groups.append(event_permission)

      self.event_broker.insert(event, False)

      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.event_broker.do_commit(commit)
      return event
    except ValidationException:
      message = ObjectValidator.getFirstValidationError(event)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an event with uuid "{1}" but the uuid already exists'.format(user.username, event.uuid))
      raise ControllerException(u'An event with uuid "{0}" already exists'.format(event.uuid))
    except BrokerException as error:
      raise ControllerException(error)

  def update_event(self, user, event, mkrelations=True, commit=True):
    self.logger.debug('User {0} updates a event {1}'.format(user.username, event.identifier))
    try:
      # the the creator

      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event, user, user.group, False)

      self.event_broker.update(event, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.event_broker.do_commit(commit)
      return event
    except ValidationException:
      message = ObjectValidator.getFirstValidationError(event)
      raise ControllerException(u'Could not update object definition due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def remove_event(self, user, event):
    self.logger.debug('User {0} deleted a event {1}'.format(user.username, event.identifier))
    try:
      self.event_broker.remove_by_id(event.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_by_id(self, identifier):
    try:
      event = self.event_broker.get_by_id(identifier)
      return event
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_by_uuids(self, id_list):
    try:
      event = self.event_broker.get_by_uuids(id_list)
      return event
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_by_uuid(self, uuid):
    try:
      event = self.event_broker.get_by_uuid(uuid)
      return event
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_all(self):
    try:
      events = self.event_broker.get_all()
      return events
    except BrokerException as error:
      raise ControllerException(error)

  def change_owner(self, event, group_id, user, commit=True):
    try:
      group = self.group_broker.get_by_id(group_id)
      user = self.user_broker.getUserByUserName(user.username)
      event.creator_group = group
      self.set_extended_logging(event, user, user.group, False)
      self.event_broker.update(event, False)
      self.event_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_user_permissions(self, event, user):
    try:
      # If is admin => give all rights the same is valid for the owenr
      isowner = is_event_owner(event, user)
      if isowner:
        permissions = EventPermissions('0')
        permissions.set_all()
      else:
        permissions = self.event_broker.get_event_user_permissions(event, user)
        permissions = permissions.permissions
      return permissions
    except NothingFoundException as error:
      self.logger.debug(error)
      # The group was not associated to the event
      # if the event is still not visible the event has to have a lower or equal tlp level
      user_tlp = user.group.tlp_lvl
      result = event.tlp.identifier >= user_tlp
      if result:
        permissions = EventPermissions('0')
        # Set to default as the user can still view
        permissions.set_default()
        return permissions
    except BrokerException as error:
      permissions = EventPermissions('0')
      return permissions

  def get_comment_by_id(self, identifer):
    try:
      return self.comment_broker.get_by_id(identifer)
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_comment_by_uuid(self, uuid):
    try:
      return self.comment_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_comment(self, user, comment):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(comment, user, user.group, True)
      self.comment_broker.insert(comment, True)
    except BrokerException as error:
      raise ControllerException(error)

  def update_comment(self, user, comment):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(comment, user, user.group, False)
      self.comment_broker.update(comment, True)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_comment(self, user, comment):
    try:
      self.comment_broker.remove_by_id(comment.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def __validate_object(self, obj, user):
    self.__validate_instance(obj, user)
    for related_object in obj.related_objects:
      self.__validate_instance(related_object.object, user)
    for attribute in obj.attributes:
      self.__validate_instance(attribute, user)

  def __validate_observable(self, observable, user):
    self.__validate_instance(observable, user)
    if observable.observable_composition:
      for child in observable.observable_composition:
        self.__validate_observable(child, user)
    if observable.object:
      self.__validate_object(observable.object, user)

  def __validate_instance(self, instance, user):
    instance.properties.is_validated = True
    self.set_extended_logging(instance, user, user.group, False)

  def validate_event(self, event, user):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event, user, user.group, False)
      self.__validate_instance(event, user)
      for observable in event.observables:
        self.__validate_observable(observable, user)
      self.event_broker.update(event, True)
    except BrokerException as error:
      raise ControllerException(error)

  def get_group_by_id(self, identifier):
    try:
      return self.group_broker.get_by_id(identifier)
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_group_by_uuid(self, uuid):
    try:
      return self.group_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_group_by_id(self, identifier):
    try:
      return self.event_broker.get_group_by_id(identifier)
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_group_by_uuid(self, uuid):
    try:
      return self.event_broker.get_group_by_uuid(uuid)
    except NothingFoundException as error:
      self.logger.debug(error)
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def insert_event_group_permission(self, user, event_group_permission, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event_group_permission, user, user.group, True)
      self.event_broker.insert_group_permission(event_group_permission, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def update_event_group_permissions(self, user, event_group_permission, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event_group_permission, user, user.group, False)
      self.event_broker.update_group_permission(event_group_permission, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_group_permissions(self, user, event_group_permission, commit=True):
    try:
      self.event_broker.remove_group_permission_by_id(event_group_permission.identifier, commit)
    except BrokerException as error:
      raise ControllerException(error)
