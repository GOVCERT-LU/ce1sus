# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.common.checks import is_event_owner
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException, ControllerIntegrityException
from ce1sus.db.brokers.event.comments import CommentBroker
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.brokers.event.reportbroker import ReferenceBroker
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException, NothingFoundException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from ce1sus.controllers.events.relations import RelationController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    super(BaseController, self).__init__(config, session)
    self.event_broker = self.broker_factory(EventBroker)
    self.comment_broker = self.broker_factory(CommentBroker)
    self.reference_broker = self.broker_factory(ReferenceBroker)
    self.relations_controller = RelationController(config, session)

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

  def insert_event(self, event, mkrelations=True, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """

    try:
      # the the creator
      # generate relations if needed!

      flat_attribtues = self.relations_controller.get_flat_attributes_for_event(event)

      if (mkrelations == 'True' or mkrelations is True) and flat_attribtues:
        self.relations_controller.generate_bulk_attributes_relations(event, flat_attribtues, False)

      self.event_broker.insert(event, False)
      self.event_broker.do_commit(commit)

      return event

    except ValidationException:
      message = ObjectValidator.getFirstValidationError(event)
      raise ControllerException(u'Could not update event due to: {0}'.format(message))
    except IntegrityException as error:
      self.logger.debug(error)
      raise ControllerIntegrityException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_event(self, event, mkrelations=True, commit=True):
    try:
      # the the creator

      # TODO relations on update

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

  def get_all_for_user(self, user):
    try:
      events = self.event_broker.get_all_for_user(user)
      return events
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_from(self, from_datetime):
    try:
      events = self.event_broker.get_all_from(from_datetime)
      return events
    except BrokerException as error:
      raise ControllerException(error)

  def __change_owner(self, instance, user, group):
    instance.creator_group = group
    self.set_extended_logging(instance, user, False)

  def __change_owner_object(self, obj, user, group):
    self.__change_owner(obj, user, group)
    for attribute in obj.attributes:
      self.__change_owner(attribute, user, group)
    for rel_obj in obj.related_objects:
      self.__change_owner_object(rel_obj.object, user, group)

  def __change_owner_observable(self, observable, user, group):
    self.__change_owner(observable, user, group)
    if observable.object:
      self.__change_owner_object(observable.object, user, group)
    if observable.observable_composition:
      for obs in observable.observable_composition.observables:
        self.__change_owner_observable(obs, user, group)

  def change_owner(self, event, group_id, user, commit=True):
    try:
      group = self.group_broker.get_by_uuid(group_id)
      user = self.user_broker.getUserByUserName(user.username)
      self.__change_owner(event, user, group)
      # TODO make change owner ship recursive
      for observable in event.observables:
        self.__change_owner_observable(observable, user, group)

      for indicator in event.indicators:
        for observable in indicator.observables:
          self.__change_owner_observable(observable, user, group)

      self.event_broker.update(event, False)
      self.event_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)

  def get_event_user_permissions(self, event, user):
    try:
      user = self.user_broker.getUserByUserName(user.username)
      # If is admin => give all rights the same is valid for the owenr
      isowner = is_event_owner(event, user)
      if isowner:
        permissions = EventPermissions('0')
        permissions.set_all()
        return permissions
      else:
        permissions = self.event_broker.get_event_user_permissions(event, user)
        if hasattr(permissions, 'permissions'):
          permissions = permissions.permissions
          return permissions
        else:
          return None

    except NothingFoundException as error:
      # The group was not associated to the event
      self.logger.debug(error)

      # if the event is still not visible the event has to have a lower or equal tlp level
      user_tlp = user.group.tlp_lvl
      result = event.tlp_level_id >= user_tlp

      if result:
        # Get the defaults for this group
        usr_grp = user.group
        permissions = usr_grp.default_permissions

      else:
        permissions = EventPermissions('0')
      return permissions
    except BrokerException as error:
      permissions = EventPermissions('0')
      return permissions

  def get_event_group_permissions(self, event, group):
    try:
      if group.identifier == event.originating_group_id:
        permissions = EventPermissions('0')
        permissions.set_all()
        return permissions
      else:
        permissions = self.event_broker.get_event_group_permissions(event, group)
        if hasattr(permissions, 'permissions'):
          permissions = permissions.permissions
          return permissions
        else:
          return None
    except NothingFoundException as error:
      # The group was not associated to the event
      self.logger.debug(error)

      # if the event is still not visible the event has to have a lower or equal tlp level
      grp_tlp = group.tlp_lvl
      result = event.tlp_level_id >= grp_tlp

      if result:
        # Get the defaults for this group
        permissions = group.default_permissions

      else:
        permissions = EventPermissions('0')
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
      self.set_extended_logging(comment, user, True)
      self.comment_broker.insert(comment, True)
    except BrokerException as error:
      raise ControllerException(error)

  def update_comment(self, user, comment):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(comment, user, False)
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
      self.__validate_object(related_object.object, user)
    for attribute in obj.attributes:
      self.__validate_instance(attribute, user)

  def __validate_observable(self, observable, user):
    self.__validate_instance(observable, user)
    if observable.observable_composition:
      observable.observable_composition.properties.is_validated = True
      for child in observable.observable_composition.observables:
        self.__validate_observable(child, user)
    if observable.object:
      self.__validate_object(observable.object, user)

  def __validate_instance(self, instance, user):
    instance.properties.is_validated = True
    self.set_extended_logging(instance, user, False)

  def validate_event(self, event, user):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event, user, False)
      self.__validate_instance(event, user)
      for observable in event.observables:
        self.__validate_observable(observable, user)
      # Validate reports
      for report in event.reports:
        self.__validate_instance(report, user)
        for reference in report.references:
          self.__validate_instance(reference, user)
      # validate indicators
      for indicator in event.indicators:
        self.__validate_instance(indicator, user)
        for observable in indicator.observables:
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
      self.set_extended_logging(event_group_permission, user, True)
      self.event_broker.insert_group_permission(event_group_permission, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def update_event_group_permissions(self, user, event_group_permission, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(event_group_permission, user, False)
      self.event_broker.update_group_permission(event_group_permission, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def remove_group_permissions(self, user, event_group_permission, commit=True):
    try:
      self.event_broker.remove_group_permission_by_id(event_group_permission.identifier, commit)
    except BrokerException as error:
      raise ControllerException(error)

  def publish_event(self, event, user):
    try:
      event.properties.is_shareable = True

      self.update_event(user, event, False, True)

    except BrokerException as error:
      raise ControllerException(error)
