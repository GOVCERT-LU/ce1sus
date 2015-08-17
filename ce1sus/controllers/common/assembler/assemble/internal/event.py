# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 31, 2015
"""
import base64
from ce1sus.helpers.common.converters import ValueConverter
from datetime import datetime
from os.path import dirname
from shutil import move, rmtree

from ce1sus.controllers.common.assembler.assemble.ccybox.ccybox import CyboxAssembler
from ce1sus.controllers.common.assembler.assemble.cstix import StixAssembler
from ce1sus.controllers.common.assembler.assemble.internal.internal import Ce1susAssembler
from ce1sus.controllers.common.basechanger import BaseChanger, AssemblerException
from ce1sus.db.brokers.definitions.referencesbroker import ReferenceDefintionsBroker
from ce1sus.db.classes.internal.event import Event, Comment, EventGroupPermission
from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.db.common.broker import NothingFoundException, BrokerException
from ce1sus.handlers.references.filehandler import FileReferenceHandler
from ce1sus.helpers.common.hash import hashMD5, fileHashSHA1
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventAssembler(BaseChanger):

  def __init__(self, config, session=None):
    super(EventAssembler, self).__init__(config, session)
    self.stix_assembler = StixAssembler(config, session)
    self.cybox_assembler = CyboxAssembler(config, session)
    self.ce1sus_assembler = Ce1susAssembler(config, session)
    self.reference_definiton_broker = self.broker_factory(ReferenceDefintionsBroker)


  def assemble_event(self, json, cache_object):
    if json:
      event = Event()

      cache_object.owner = True

      self.set_base(event, json, cache_object, None)

      event.id_ = json.get('id_', None)
      event.idref = json.get('idref', None)

      version = json.get('version', None)
      event.version = Version(version, event)



      stix_header = json.get('stix_header', None)
      if stix_header:
        event.stix_header = self.stix_assembler.assemble_stix_header(event, stix_header, cache_object)


      first_seen = json.get('first_seen', None)
      if first_seen:
        first_seen = ValueConverter.set_date(first_seen)
      else:
        first_seen = datetime.utcnow()
      event.first_seen = first_seen
      last_seen = json.get('last_seen', None)
      if last_seen:
        last_seen = ValueConverter.set_date(last_seen)
      else:
        last_seen = datetime.utcnow()
      event.last_seen = last_seen
      # TODO: decide if to set last publish date?!
      """
      last_publish_date = json.get('last_publish_date', None)
      if last_publish_date:
        last_publish_date = ValueConverter.set_date(last_publish_date)
      event.last_publish_date = last_publish_date
      """

      event.risk = json.get('risk', 'Undefined').title()
      event.status = json.get('status', 'Draft').title()
      event.tlp = json.get('tlp', 'Amber').title()
      event.analysis = json.get('analysis', 'Unknown').title()

      # TODO: create assembler for the new stix elements
      """
      campaigns = json.get('campaigns', None)
      for campaign in campaigns:
        campaign = self.stix_assembler.assemble_campaign(campaign, user, seen_groups, rest_insert, owner)
        if campaign:
          event.campaigns.append(campaign)

      exploit_targets = json.get('exploit_targets', None)
      for exploit_target in exploit_targets:
        exploit_target = self.stix_assembler.assemble_exploit_target(exploit_target, user, seen_groups, rest_insert, owner)
        if exploit_target:
          event.exploit_targets.append(exploit_target)
      """

      observables = json.get('observables', None)
      if observables:
        for observable in observables:
          observable = self.cybox_assembler.assemble_observable(event, observable, cache_object)
          if observable:
            event.observables.append(observable)

      indicators = json.get('indicators', None)
      if indicators:
        for indicator in indicators:
          indicator = self.stix_assembler.assemble_indicator(indicator, cache_object)
          if indicator:
            event.indicators.append(indicator)
      """
      incidents = json.get('incidents', None)
      for incident in incidents:
        incident = self.stix_assembler.assemble_incident(incident, user, seen_groups, rest_insert, owner)
        if incident:
          event.incidents.append(incident)

      threat_actors = json.get('threat_actors', None)
      for threat_actor in threat_actors:
        threat_actor = self.stix_assembler.assemble_threat_actor(threat_actor, user, seen_groups, rest_insert, owner)
        if threat_actor:
          event.threat_actors.append(threat_actor)

      ttps = json.get('ttps', None)
      for ttp in ttps:
        ttp = self.stix_assembler.assemble_ttp(ttp, user, seen_groups, rest_insert, owner)
        if ttp:
          event.ttps.append(ttp)

      related_packages = json.get('related_packages', None)
      for related_package in related_packages:
        related_package = self.stix_assembler.assemble_related_package(related_package, user, seen_groups, rest_insert, owner)
        if related_package:
          event.related_packages.append(related_package)
      """
      reports = json.get('reports', None)
      if reports:
        for report in reports:
          report = self.assemble_report(event, report, cache_object)
          if report:
            event.reports.append(report)

      comments = json.get('comments', None)
      if comments:
        for comment in comments:
          com = self.assemble_comment(event, comment, cache_object)
          if com:
            event.comments.append(com)

      # add the eventGroupPermissions from the event
      event_permissions = json.get('groups', None)
      if event_permissions:
        for event_permission in event_permissions:
          ev_perm = self.assemble_group_permision(event, event_permission, cache_object)
          if ev_perm and not ev_perm.group.equals(event.creator_group):
            event.groups.append(ev_perm)

      return event

  def assemble_report(self, event, json, cache_object):
    report = Report()

    self.set_base(report, json, cache_object, event)
    report.title = json.get('title', None)
    report.description = json.get('description', None)
    report.short_description = json.get('short_description', None)
    # link event
    report.event = event
    references = json.get('references', None)
    if references:
      for reference in references:
        ref = self.assemble_reference(report, reference, cache_object)
        if ref:
          report.references.append(ref)

    related_reports = json.get('related_reports', None)
    if related_reports:
      for related_report in related_reports:
        related_report = self.assemble_report(related_report, json, cache_object)
        if related_report:
          related_report.parent_report = report
          related_report.event = None
          report.related_reports.append(related_report)

    return report

  def get_reference_definition(self, json, seen_ref_defs):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition_json = json.get('definition', None)
      if definition_json:
        uuid = definition_json.get('identifier', None)
    if uuid:
      rd = seen_ref_defs.get(uuid, None)
      if rd:
        return rd
      else:
        try:
          definition = self.reference_definiton_broker.get_by_uuid(uuid)
          seen_ref_defs[uuid] = definition
        except NothingFoundException as error:
          raise AssemblerException(error)
        except BrokerException as error:
          raise AssemblerException(error)

        return definition
    raise AssemblerException('Could not find "{0}" definition in the reference'.format(definition_json))

  def assemble_reference(self, report, json, cache_object):

    if json:
      value = json.get('value', None)
      if value:
        definition = self.get_reference_definition(json, cache_object.seen_ref_defs)
        if definition:
          ref = Reference()
          self.set_base(ref, json, cache_object, report)
          ref.definition_id = definition.identifier
          # TODO: find a better way to embed the handlers
          handler_uuid = '{0}'.format(definition.reference_handler.uuid)
          if handler_uuid in ['0be5e1a0-8dec-11e3-baa8-0800200c9a66']:

            fh = FileReferenceHandler()
            filename = value.get('filename', None)
            data = value.get('data', None)
            if filename and data:
              tmp_filename = hashMD5(datetime.utcnow())
              binary_data = base64.b64decode(data)
              tmp_folder = fh.get_tmp_folder()
              tmp_path = tmp_folder + '/' + tmp_filename

              file_obj = open(tmp_path, "w")
              file_obj.write(binary_data)
              file_obj.close()

              sha1 = fileHashSHA1(tmp_path)
              rel_folder = fh.get_rel_folder()
              dest_path = fh.get_dest_folder(rel_folder) + '/' + sha1

              # move it to the correct place
              move(tmp_path, dest_path)
              # remove temp folder
              rmtree(dirname(tmp_path))

              ref.value = rel_folder + '/' + sha1 + '|' + filename
            else:
              raise AssemblerException('Reference file is malformated')
          else:
            ref.value = value

          return ref
        else:
          return None
      else:
        return None

  def assemble_comment(self, event, json, cache_object):

    if json:
      comment = Comment()
      self.set_base(comment, json, cache_object, event)
      comment.comment = json.get('comment', None)
      if comment.comment:
        comment.event = event
        return comment

  def assemble_group_permision(self, event, json, cache_object):

    if json:
      event_permission = EventGroupPermission()
      self.set_base(event_permission, json, cache_object, event)
      permissions = json.get('permissions', None)
      if permissions:
        event_permission.permissions = self.ce1sus_assembler.assemble_permissions(permissions, cache_object)

      group_json = json.get('group', None)
      if group_json:
        group = self.get_set_group(group_json, cache_object, True)
        if not group:
          group = self.ce1sus_assembler.assemble_group(group_json, cache_object)
        event_permission.group = group
      if event_permission.group:
        return event_permission
