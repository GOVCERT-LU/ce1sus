# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 8, 2015
"""
from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.observables import Observable
from ce1sus.db.classes.report import Report


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MergingException(Exception):
  pass


class Merger(BaseController):

  def set_dbcode(self, local, remote):
    self.logger.info('{0} {1} dbcode will be replaced "{2}" by "{3}"'.format(local.__class__.__name__, local.uuid, local.dbcode, local.dbcode))
    # set only share and proposal
    local.properties.is_shareable = remote.properties.is_shareable
    local.properties.is_proposal = remote.properties.is_proposal
    # unvalidate only if the value has changed
    if hasattr(local, 'value'):
      if local.value == remote.value:
        local.properties.is_validated = True
      else:
        local.properties.is_validated = False

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)

  def append_object(self, remote_object, local_event, local_observable, parent):
    remote_object.observable = local_observable
    remote_object.observable_id = local_observable.identifier
    if isinstance(parent, Observable):
      remote_object.parent = parent
      remote_object.parent.identifier = parent.identifier
    else:
      remote_object.parent = None
      remote_object.parent.identifier = None

    for attribute in remote_object.attributes:
      attribute.value_instance.event = local_event
      attribute.value_instance.event_id = local_event.identifier
    if remote_object.related_objects:
      for rel_obj in remote_object.related_objects:
        self.append_object(rel_obj.object, local_event, rel_obj, local_observable, remote_object)

  def append_observable(self, remote_observable, local_event, parent):
    # be sure that the remote_observable links to the local_event
    remote_observable.parent = local_event
    remote_observable.parent_id = local_event.identifier
    if isinstance(parent, Event):
      remote_observable.event = local_event
      remote_observable.event_id = local_event.identifier
    else:
      remote_observable.event = None
      remote_observable.event_id = None
    # check and append its children
    if remote_observable.object:
      self.append_object(remote_observable.object, local_event, remote_observable, remote_observable)
    if remote_observable.observable_composition:
      for observable in remote_observable.observable_composition.observables:
        # TODO find parent
        self.append_observable(observable, local_event, None)
    if remote_observable.related_observables:
      for rel_observable in remote_observable.related_observables:

        pass
        # TODO related observables
        # self.append_related_observable(rel_observable, local_event, remote_observable)

    if hasattr(parent, 'observables'):
      parent.observables.append(remote_observable)

  def append_attribute(self, local_object, attribute):
    event = local_object.event
    attribute.value_instance.event = event
    attribute.value_instance.event_id = event.identifier
    local_object.attributes.append(attribute)

  def merge_attribute(self, local_attribute, rem_attribute, user):
    if local_attribute.modified_on < rem_attribute.modified_on:
      self.logger.info('Attribute {0} will be updated'.format(local_attribute.uuid))
      self.set_dbcode(local_attribute, rem_attribute)
      self.logger.info('Attribute {0} is_ioc will be replaced "{1}" by "{2}"'.format(local_attribute.uuid, local_attribute.is_ioc, rem_attribute.is_ioc))
      local_attribute.is_ioc = rem_attribute.is_ioc
      self.logger.info('Attribute {0} condition_id will be replaced "{1}" by "{2}"'.format(local_attribute.uuid, local_attribute.condition_id, rem_attribute.condition_id))
      local_attribute.condition_id = rem_attribute.condition_id
      self.logger.info('Attribute {0} value will be replaced "{1}" by "{2}"'.format(local_attribute.uuid, local_attribute.value, rem_attribute.value))
      local_attribute.value = rem_attribute.value
      local_attribute.modified_on = rem_attribute.modified_on
      local_attribute.modifier_id = user.identifier
      return True
    return False

  def merge_object(self, local_object, remote_object, parent, user):
    merges = False
    if local_object.modified_on < remote_object.modified_on:
      self.logger.info('Object {0} will be updated'.format(local_object.uuid))
      self.set_dbcode(local_object, remote_object)
      local_object.modified_on = remote_object.modified_on
      local_object.modifier_id = user.identifier
      merges = True

    for rem_attribute in remote_object.attributes:
      # find the corresponding one
      found = False
      for local_attribute in local_object.attributes:
        if self.is_attribute_the_same(rem_attribute, local_attribute):
          merged_attr = self.merge_attribute(local_attribute, rem_attribute, user)
          if not merges:
            merges = merged_attr
          found = True
      if not found:
        # it is a new attribute
        self.append_attribute(local_object, rem_attribute)
        merges = True

    for rem_related_object in remote_object.related_objects:
      found = False
      for local_related_object in local_object.related_objects:
        if self.is_object_the_same(local_related_object, rem_related_object):
          merged_attr = self.merge_object(local_related_object.object, rem_related_object.object, local_related_object, user)
          if not merges:
            merges = merged_attr
          found = True
      if not found:
        self.append_related_object(rem_related_object, local_object)
        merges = True

    return merges

  def is_object_the_same(self, local_related_object, rem_related_object):
    if rem_related_object.uuid == local_related_object.uuid:
      return True
    else:
      # maybe the there is an attribute which is the same
      for rem_attr in rem_related_object.attributes:
        for local_attr in local_related_object.attributes:
          if self.is_attribute_the_same(rem_attr, local_attr):
            return True
      return False

  def append_related_object(self, rem_related_object, local_object):
    rem_related_object.parent = local_object
    rem_related_object.parent_id = local_object.identifier
    self.append_object(rem_related_object.object, local_object.event, local_object.observable, local_object)

  def merge_observable(self, local_observable, remote_observable, user):
    merges = False
    if local_observable.modified_on < remote_observable.modified_on:
      self.logger.info('Observable {0} will be updated'.format(local_observable.uuid))
      self.logger.info('Observable {0} title will be replaced "{1}" by "{2}"'.format(local_observable.uuid, local_observable.title, remote_observable.title))
      local_observable.title = remote_observable.title
      self.logger.info('Observable {0} description will be replaced "{1}" by "{2}"'.format(local_observable.uuid, local_observable.description, remote_observable.description))
      local_observable.description = remote_observable.description
      self.logger.info('Observable {0} version will be replaced "{1}" by "{2}"'.format(local_observable.uuid, local_observable.version, remote_observable.version))
      local_observable.version = remote_observable.version
      self.set_dbcode(local_observable, remote_observable)
      local_observable.modified_on = remote_observable.modified_on
      local_observable.modifier_id = user.identifier

      merges = True
    # merge objects
    if local_observable.object or remote_observable.object:
      obj_merge = self.merge_object(local_observable.object, remote_observable.object, local_observable, user)
      if not merges:
        merges = obj_merge
    if local_observable.observable_composition or remote_observable.observable_composition:
      obj_merge = self.merge_observable_composition(local_observable.observable_composition, remote_observable.observable_composition, local_observable, local_observable.parent, user)
      if not merges:
        merges = obj_merge

    # TODO merge related observables

    return merges

  def merge_observable_composition(self, local_observable_composition, remote_observable_composition, parent, local_event, user):
    merges = False

    self.logger.info('Observable Composition {0} will be updated'.format(local_observable_composition.uuid))
    self.set_dbcode(local_observable_composition, remote_observable_composition)
    if remote_observable_composition.operator:
      self.logger.info('Observable Composition {0} operator will be replaced "{1}" by "{2}"'.format(local_observable_composition.uuid, local_observable_composition.operator, remote_observable_composition.operator))
      local_observable_composition.operator = remote_observable_composition.operator
    merges = True
    for rem_obs in remote_observable_composition.observables:
      # find the corresponding one
      found = False
      for local_obs in local_observable_composition.observables:
        if self.is_observable_the_same(local_obs, rem_obs):
          merged_attr = self.merge_observable(local_obs, rem_obs, user)
          if not merges:
            merges = merged_attr
          found = True
      if not found:
        # it is a new attribute
        self.append_observable(rem_obs, local_event, local_observable_composition)
        merges = True

    return merges

  def is_observable_the_same(self, local_observable, remote_observable):
    if local_observable.uuid == remote_observable.uuid:
      return True
    else:
      if local_observable.object:
        return self.is_object_the_same(local_observable.object, remote_observable.object)
      else:
        if remote_observable.observable_composition:
          for rem_obs in remote_observable.observable_composition.observables:
            same = False
            for local_obs in local_observable.observable_composition.observables:
              same = self.is_observable_the_same(local_obs, rem_obs)
              if same:
                return True
    return False

  def merge_observables(self, local_observables, remote_observables, local_event, parent, user):
    merges = False
    for remote_observable in remote_observables:
      # find the corresponding one in local_observables:
      found = False
      for local_observable in local_observables:
        if self.is_observable_the_same(local_observable, remote_observable):
          obs_merge = self.merge_observable(local_observable, remote_observable, user)
          if not merges:
            merges = obs_merge
          found = True
          break
      if not found:
        # observable is new add it
        self.append_observable(remote_observable, local_event, parent)
        merges = True

    return merges

  def merge_events(self, local_event, remote_event, user):
    # check which one is newer (utc is ignored as everything is in utc)
    merges = False
    if remote_event.modified_on > local_event.modified_on:
      # take over all values and log the old ones to log
      self.logger.info('Event {0} will be updated'.format(local_event.uuid))
      self.logger.info('Event {0} title will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.title, remote_event.title))
      local_event.title = remote_event.title
      self.logger.info('Event {0} description will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.description, remote_event.description))
      local_event.description = remote_event.description
      self.logger.info('Event {0} tlp_level_id will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.tlp_level_id, remote_event.tlp_level_id))
      local_event.tlp_level_id = remote_event.tlp_level_id
      self.logger.info('Event {0} status_id will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.status_id, remote_event.status_id))
      local_event.status_id = remote_event.status_id
      self.logger.info('Event {0} risk_id will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.risk_id, remote_event.risk_id))
      local_event.risk_id = remote_event.risk_id
      self.logger.info('Event {0} analysis_id will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.analysis_id, remote_event.analysis_id))
      local_event.analysis_id = remote_event.analysis_id
      self.set_dbcode(local_event, local_event)
      # event will get unpublished
      local_event.properties.is_shareable = False
      self.logger.info('Event {0} title will be replaced "{1}" by "{2}"'.format(local_event.uuid, local_event.last_publish_date, remote_event.last_publish_date))
      local_event.last_publish_date = remote_event.last_publish_date

      local_event.modified_on = remote_event.modified_on
      local_event.modifier_id = user.identifier

      merges = True

    obs_merges = self.merge_observables(local_event.observables, remote_event.observables, local_event, local_event, user)
    if not merges:
      merges = obs_merges

    # TODO merge indicators

    obs_merges = self.merge_reports(local_event.reports, remote_event.reports, local_event, local_event, user)
    if not merges:
      merges = obs_merges

    if merges:
      return local_event
    else:
      return None

  def merge_report(self, local_report, remote_report, local_event, parent, user):
    merges = False
    if remote_report.modified_on > local_report.modified_on:
      # take over all values and log the old ones to log
      self.logger.info('Report {0} will be updated'.format(local_event.uuid))
      self.logger.info('Report {0} title will be replaced "{1}" by "{2}"'.format(local_report.uuid, local_report.title, remote_report.title))
      local_report.title = remote_report.title
      self.logger.info('Report {0} description will be replaced "{1}" by "{2}"'.format(local_report.uuid, local_report.description, remote_report.description))
      local_report.description = remote_report.description
      self.logger.info('Report {0} short_description will be replaced "{1}" by "{2}"'.format(local_report.uuid, local_report.short_description, remote_report.short_description))
      local_report.short_description = remote_report.short_description
      self.set_dbcode(local_report, remote_report)
      self.logger.info('Report {0} title will be replaced "{1}" by "{2}"'.format(local_report.uuid, local_report.title, remote_report.title))
      local_report.title = remote_report.title
      local_report.modified_on = remote_report.modified_on
      local_report.modifier_id = user.identifier
    for rem_reference in remote_report.references:
      # find the corresponding one
      found = False
      for local_reference in local_report.references:
        if self.is_reference_the_same(rem_reference, local_reference):
          merged_attr = self.merge_reference(local_reference, rem_reference, user)
          if not merges:
            merges = merged_attr
          found = True
      if not found:
        # it is a new reference
        self.append_reference(rem_reference, local_report)
        merges = True

    # TODO related reports
    return merges

  def merge_reference(self, local_reference, rem_reference, user):
    if local_reference.modified_on < rem_reference.modified_on:
      self.logger.info('Reference {0} will be updated'.format(local_reference.uuid))
      self.set_dbcode(local_reference, rem_reference)
      self.logger.info('Reference {0} value will be replaced "{1}" by "{2}"'.format(local_reference.uuid, local_reference.value, rem_reference.value))
      local_reference.value = rem_reference.value
      local_reference.modified_on = rem_reference.modified_on
      local_reference.modifier_id = user.identifier
      return True
    return False

  def append_reference(self, reference, local_report):
    reference.report = local_report
    reference.report_id = local_report.identifier
    local_report.references.append(reference)

  def append_report(self, remote_report, local_event, parent):
    remote_report.event = local_event
    remote_report.event_id = local_event.identifier
    if isinstance(parent, Report):
      remote_report.parent_report = parent
      remote_report.parent_report_id = parent.identifier
    else:
      remote_report.parent_report = None
      remote_report.parent_report_id = None
    parent.reports.append(remote_report)

  def is_report_same(self, local_report, remote_report):
    if local_report.uuid == remote_report.uuid:
      return True
    else:
      for rem_ref in remote_report.references:
        for local_ref in local_report.references:
          same = self.is_reference_the_same(rem_ref, local_ref)
          if same:
            return True
    return False

  def is_reference_the_same(self, rem_ref, local_ref):
    if rem_ref.uuid == local_ref.uuid:
      return True
    else:
      if rem_ref.value == local_ref.value:
        return True
    return False

  def is_attribute_the_same(self, rem_attr, local_attr):
    if rem_attr.uuid == local_attr.uuid:
      return True
    else:
      if rem_attr.value == local_attr.value:
        return True
    return False

  def merge_reports(self, local_reports, remote_reports, local_event, parent, user):
    merges = False
    for remote_report in remote_reports:
      # find the corresponding one in local_observables:
      found = False
      for local_report in local_reports:
        if self.is_report_same(local_report, remote_report):
          obs_merge = self.merge_report(local_report, remote_report, local_event, parent, user)
          if not merges:
            merges = obs_merge
          found = True
          break
      if not found:
        # observable is new add it
        self.append_report(remote_report, local_event, parent)
        merges = True
    # TODO merge related reports

    return merges
