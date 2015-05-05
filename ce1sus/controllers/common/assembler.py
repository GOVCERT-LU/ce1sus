# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 18, 2015
"""
from datetime import datetime

from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.brokers.definitions.referencesbroker import ReferenceDefintionsBroker, ReferencesBroker
from ce1sus.db.brokers.definitions.typebrokers import AttributeTypeBroker
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.db.classes.event import Comment, Event
from ce1sus.db.classes.group import Group
from ce1sus.db.classes.object import Object, RelatedObject
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.db.classes.report import Report, Reference, ReferenceDefinition
from ce1sus.db.classes.servers import SyncServer
from ce1sus.db.classes.user import User
from ce1sus.db.common.broker import BrokerException, NothingFoundException
from ce1sus.helpers.common import strings


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AssemblerException(Exception):
  pass


class Assembler(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.observable_controller = ObservableController(config, session)
    self.event_controller = EventController(config, session)
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.reference_definiton_broker = self.broker_factory(ReferenceDefintionsBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)
    self.value_type_broker = self.broker_factory(AttributeTypeBroker)
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.references_broker = self.broker_factory(ReferencesBroker)

  def get_user(self, json):
    uuid = json.get('identifier', None)
    if uuid:
      try:
        return self.user_broker.get_by_uuid(uuid)
      except BrokerException:
        return None
    else:
      return None

  def get_db_user(self, user):
    try:
      return self.user_broker.get_by_id(user.identifier)
    except BrokerException as error:
      raise ControllerException(error)

  def update_syncserver(self, server, json):
    server.populate(json)
    user_uuid = json.get('user_id', None)
    if not user_uuid:
      user = json.get('user', None)
      user_uuid = user.get('identifier', None)
    if user_uuid:
      user = self.user_broker.get_by_uuid(user_uuid)
      server.user = user
      server.user_id = user.identifier

  def populate_simple_logging(self, instance, json, user, insert=False):
    db_user = self.get_db_user(user)
    if insert:
      # Note the creator

      instance.creator_id = db_user.identifier
      instance.creator = db_user

      created_at = json.get('created_at', None)
      if created_at:
        instance.created_at = strings.stringToDateTime(created_at)
      else:
        instance.created_at = datetime.utcnow()

    instance.modifier_id = db_user.identifier
    instance.modifier = db_user
    instance.modified_on = datetime.utcnow()

  def get_set_group(self, json, user):
    """ If the group does not exist or cannot be created return the users group"""
    group = None
    if json:

      # check if group exists
      uuid = json.get('identifier', None)
      if uuid:
        try:
          group = self.group_broker.get_by_uuid(uuid)
        except NothingFoundException:
          # Create the group automatically
          group = Group()
          group.populate(json)
          group.uuid = uuid
          self.group_broker.insert(group, False)
          return group
        except BrokerException:
          group = None
      else:
        name = json.get('name', None)
        if name:
          try:
            group = self.group_broker.get_by_name(name)
          except NothingFoundException:
            group = Group()
            group.populate(json)
            self.group_broker.insert(group, False)
            return group
    if not group:
      try:
        group = self.group_broker.get_by_id(user.group_id)
      except BrokerException as error:
        raise ControllerException(error)

    return group

  def populate_extended_logging(self, instance, json, user, insert=False):
    self.populate_simple_logging(instance, json, user, insert)
    if insert:
      instance.creator_group = self.get_set_group(json.get('creator_group', None), user)
      instance.originating_group = self.get_set_group(json.get('originating_group', None), user)

  def assemble_event(self, json, user, owner=False, rest_insert=True, poponly=False):

    event = Event()
    event.populate(json, rest_insert)
    event.uuid = json.get('identifier', None)
    self.populate_extended_logging(event, json, user, True)

    if not poponly:
      self.event_controller.insert_event(user, event, True, False)

    if owner:
      event.properties.is_validated = True
      event.properties.is_proposal = False
    else:
      event.properties.is_validated = False
      event.properties.is_proposal = True

    observables = json.get('observables', None)
    if observables:
      for observable in observables:
        obs = self.assemble_observable(event, observable, user, owner, rest_insert)
        event.observables.append(obs)
    reports = json.get('reports', None)
    if reports:
      for report in reports:
        rep = self.assemble_report(event, report, user, owner, rest_insert)
        if rep:
          event.reports.append(rep)
    comments = json.get('comments', None)
    if comments:
      for comment in comments:
        com = self.assemble_comment(event, comment, user, owner, rest_insert)
        event.comments.append(com)
    # TODO check if definitions do exist
    event.properties.is_rest_instert = rest_insert
    event.properties.is_web_insert = not rest_insert
    return event

  def update_event(self, event, json, user, owner=False, rest_insert=True):
    event.populate(json, rest_insert)
    # TODO merge here
    self.populate_extended_logging(event, json, user, False)
    return event

  def assemble_comment(self, event, json, user, owner=False, rest_insert=True):
    comment = Comment()
    comment.uuid = json.get('identifier', None)
    comment.populate(json, rest_insert)
    self.populate_extended_logging(comment, json, user, True)
    comment.event_id = event.identifier

    if owner:
      comment.properties.is_validated = True
      comment.properties.is_proposal = False
    else:
      comment.properties.is_validated = False
      comment.properties.is_proposal = True

    comment.properties.is_rest_instert = rest_insert
    comment.properties.is_web_insert = not rest_insert
    return comment

  def update_comment(self, comment, json, user, owner=False, rest_insert=True):
    comment.populate(json, rest_insert)
    self.populate_extended_logging(comment, json, user, False)
    return comment

  def assemble_composed_observable(self, event, json, user, owner=False, rest_insert=True):
    composed = ObservableComposition()
    composed.uuid = json.get('identifier', None)
    composed.operator = json.get('operator', 'OR')
    observables = json.get('observables', None)

    if observables:
      for observable in observables:
        obs = self.assemble_observable(event, observable, user, owner, rest_insert)
        obs.event_id = None
        composed.observables.append(obs)
    composed.properties.populate(json.get('properties'))
    if owner:
      composed.properties.is_validated = True
      composed.properties.is_proposal = False
    else:
      composed.properties.is_validated = False
      composed.properties.is_proposal = True

    return composed

  def assemble_observable(self, event, json, user, owner=False, rest_insert=True):

    observable = Observable()
    observable.uuid = json.get('identifier', None)
    observable.event_id = event.identifier
    observable.populate(json, rest_insert)
    observable.parent_id = event.identifier
    self.populate_extended_logging(observable, json, user, True)

    self.observable_controller.insert_observable(observable, user, False)
    # check if it is a composed one or not
    composed_obs = json.get('observable_composition', None)
    if composed_obs:
      composed = self.assemble_composed_observable(event, composed_obs, user, owner, rest_insert)
      observable.observable_composition = composed
    else:
      obj = json.get('object')
      if obj:
        observable.object = self.assemble_object(observable, obj, user, owner, rest_insert)

    rel_observables = json.get('related_observables', None)
    if rel_observables:
      raise Exception('Not yet implemented')
    if owner:
      observable.properties.is_validated = True
      observable.properties.is_proposal = False
    else:
      observable.properties.is_validated = False
      observable.properties.is_proposal = True

    observable.properties.is_rest_instert = rest_insert
    observable.properties.is_web_insert = not rest_insert
    return observable

  def update_observable(self, observable, json, user, owner=False, rest_insert=True):
    observable.populate(json, rest_insert)
    self.populate_extended_logging(observable, json, user, False)
    return observable

  def get_object_definition(self, json):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      try:
        definition = self.obj_def_broker.get_by_uuid(uuid)
      except NothingFoundException as error:
        raise ControllerNothingFoundException(error)
      except BrokerException as error:
        raise ControllerException(error)
      return definition
    raise ControllerException('Could not find a definition in the object')

  def get_attribute_definition(self, json):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      try:
        definition = self.attr_def_broker.get_by_uuid(uuid)
      except NothingFoundException as error:
        raise ControllerNothingFoundException(error)
      except BrokerException as error:
        raise ControllerException(error)
      return definition
    raise ControllerException('Could not find a definition in the attribute')

  def assemble_object(self, observable, json, user, owner=False, rest_insert=True):

    obj = Object()
    obj.uuid = json.get('identifier', None)
    self.populate_extended_logging(obj, json, user, True)

    obj.populate(json, rest_insert)

    # set definition
    definition = self.get_object_definition(json)
    obj.definition = definition
    obj.definition_id = definition.identifier

    obj.observable_id = observable.identifier
    obj.observable = observable
    obj.parent = observable
    obj.parent_id = observable.identifier

    if owner:
      obj.properties.is_validated = True
      obj.properties.is_proposal = False
    else:
      obj.properties.is_validated = False
      obj.properties.is_proposal = True

    self.observable_controller.insert_object(obj, user, False)

    rel_objs = json.get('related_objects', None)
    if rel_objs:
      for rel_obj in rel_objs:
        rel_obj_inst = self.assemble_related_object(obj, rel_obj, user, owner, rest_insert)
        obj.related_objects.append(rel_obj_inst)

    attributes = json.get('attributes')
    if attributes:
      for attribute in attributes:
        attr = self.assemble_attribute(obj, attribute, user, owner, rest_insert)
        obj.attributes.append(attr)
    obj.properties.is_rest_instert = rest_insert
    obj.properties.is_web_insert = not rest_insert
    return obj

  def assemble_serversync(self, json):
    server = SyncServer()
    server.populate(json)
    user_uuid = json.get('user_id', None)
    if not user_uuid:
      user = json.get('user', None)
      user_uuid = user.get('identifier', None)
    if user_uuid:
      user = self.user_broker.get_by_uuid(user_uuid)
      server.user = user
      server.user_id = user.identifier
    return server

  def assemble_attribute(self, obj, json, user, owner=False, rest_insert=True):
    attribute = Attribute()
    attribute.uuid = json.get('identifier', None)

    definition = self.get_attribute_definition(json)
    attribute.definition = definition
    attribute.definition_id = definition.identifier

    attribute.object = obj
    attribute.object_id = obj.identifier

    attribute.value = json.get('value', None)

    condition_uuid = json.get('condition_id', None)
    if not condition_uuid:
      condition = json.get('condition', None)
      if condition:
        condition_uuid = condition.get('identifier', None)
    if condition_uuid:
      condition = self.condition_broker.get_by_uuid(condition_uuid)
      self.condition_id = condition.identifier
    attribute.is_ioc = json.get('ioc', 0)
    attribute.properties.populate(json.get('properties', None))
    attribute.properties.is_rest_instert = rest_insert
    attribute.properties.is_web_insert = not rest_insert

    self.populate_extended_logging(attribute, json, user, True)
    if owner:
      attribute.properties.is_validated = True
      attribute.properties.is_proposal = False
    else:
      attribute.properties.is_validated = False
      attribute.properties.is_proposal = True
    return attribute

  def assemble_attribute_definition(self, json):
    attr_def = AttributeDefinition()

    return self.update_attribute_definition(attr_def, json)

  def assemble_reference_definition(self, json):
    ref_def = ReferenceDefinition()
    return self.update_reference_definition(ref_def, json)

  def update_reference_definition(self, ref_def, json):
    ref_def.populate(json)
    referencehandler_uuid = json.get('referencehandler_id', None)
    if referencehandler_uuid:
      referencehandler = self.references_broker.get_handler_by_uuid(referencehandler_uuid)
      ref_def.referencehandler_id = referencehandler.identifier
      ref_def.referencehandler = referencehandler
    else:
      raise AssemblerException('Reference definition does not have a handler specified')
    return ref_def

  def update_attribute_definition(self, attr_def, json):
    attr_def.populate(json)

    attributehandler_uuid = json.get('attributehandler_id', None)
    if attributehandler_uuid:
      attribute_handler = self.handler_broker.get_by_uuid(attributehandler_uuid)
      attr_def.attributehandler_id = attribute_handler.identifier
      attr_def.attribute_handler = attribute_handler
    else:
      raise AssemblerException('Attribute definition does not have a handler specified')

    value_type_uuid = json.get('type_id', None)

    if value_type_uuid:
      value_type = self.value_type_broker.get_by_uuid(value_type_uuid)
      attr_def.value_type_id = value_type.identifier
      attr_def.value_type = value_type
    else:
      raise AssemblerException('Attribute definition does not have a value type specified')

    default_condition_uuid = json.get('default_condition_id', None)
    if default_condition_uuid:
      default_condition = self.condition_broker.get_by_uuid(default_condition_uuid)
      attr_def.default_condition_id = default_condition.identifier
      attr_def.default_condition = default_condition
    else:
      raise AssemblerException('Attribute definition does not have a condition specified')

    return attr_def

  def assemble_user(self, json):
    user = User()
    return self.update_user(user, json)

  def update_user(self, user, json):
    user.populate(json)
    group_uuid = json.get('group_id', None)
    if group_uuid:
      group = self.group_broker.get_by_uuid(group_uuid)
      user.group_id = group.identifier
      user.group = group
    else:
      user.group_id = None
      user.group = None
    return user

  def update_object(self, obj, json, user, owner=False, rest_instert=True):
    obj.populate(json, rest_instert)
    self.populate_extended_logging(obj, json, user, False)
    return obj

  def assemble_related_object(self, obj, json, user, owner=False, rest_insert=True):

    child_obj_json = json.get('object')
    child_obj = self.assemble_object(obj.observable, child_obj_json, user, owner, rest_insert)
    # dereference object from observable
    child_obj.parent = None
    child_obj.parent_id = None
    # update parent
    related_object = RelatedObject()
    related_object.parent_id = obj.identifier
    related_object.child_id = child_obj.identifier
    related_object.object = child_obj
    related_object.relation = json.get('relation', None)
    if related_object.relation == 'None':
      related_object.relation = None
    obj.related_objects.append(related_object)
    if owner:
      related_object.properties.is_validated = True
      related_object.properties.is_proposal = False
    else:
      related_object.properties.is_validated = False
      related_object.properties.is_proposal = True
    return related_object

  def get_reference_definition(self, json):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition_json = json.get('definition', None)
      if definition_json:
        uuid = definition_json.get('identifier', None)
    if uuid:
      try:
        definition = self.reference_definiton_broker.get_by_uuid(uuid)
      except NothingFoundException as error:
        raise ControllerNothingFoundException(error)
      except BrokerException as error:
        raise ControllerException(error)
      return definition
    raise ControllerException('Could not find "{0}" definition in the reference'.format(definition_json))

  def assemble_reference(self, reference, user, owner, rest_insert=True):
    value = reference.get('value', None)
    if value:
      definition = self.get_reference_definition(reference)
      if definition:
        ref = Reference()
        ref.definition = definition
        ref.uuid = reference.get('identifier', None)
        ref.populate(reference, rest_insert)
        # set definition
        self.populate_extended_logging(ref, reference, user, True)
        if owner:
          ref.properties.is_validated = True
          ref.properties.is_proposal = False
        else:
          ref.properties.is_validated = False
          ref.properties.is_proposal = True
        ref.properties.is_rest_instert = rest_insert
        ref.properties.is_web_insert = not rest_insert
        return ref
      else:
        return None
    else:
      return None

  def assemble_report(self, event, json, user, owner=False, rest_insert=True):
    report = Report()
    report.uuid = json.get('identifier', None)
    report.populate(json, rest_insert)
    report.event_id = event.identifier
    self.populate_extended_logging(report, json, user, True)
    report.event = event
    if owner:
      report.properties.is_validated = True
      report.properties.is_proposal = False
    else:
      report.properties.is_validated = False
      report.properties.is_proposal = True
    references = json.get('references', list())
    for reference in references:
      ref = self.assemble_reference(reference, user, owner, rest_insert)
      report.references.append(ref)

    report.properties.is_rest_instert = rest_insert
    report.properties.is_web_insert = not rest_insert
    return report

  def update_report(self, report, json, user, owner=False, rest_insert=True):
    report.populate(json)
    self.populate_extended_logging(report, json, user, False)
    return report
