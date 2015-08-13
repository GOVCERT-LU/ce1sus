# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 18, 2015
"""
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.assembler.assemble.ccybox.ccybox import CyboxAssembler
from ce1sus.controllers.common.assembler.assemble.cstix import StixAssembler
from ce1sus.controllers.common.assembler.assemble.internal.event import EventAssembler
from ce1sus.controllers.common.assembler.assemble.internal.internal import Ce1susAssembler
from ce1sus.controllers.common.basecontroller import BaseChangeController
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.internal.attributes.attribute import Condition
from ce1sus.db.classes.internal.backend.servers import SyncServer
from ce1sus.db.classes.internal.backend.types import AttributeType
from ce1sus.db.classes.internal.definitions import AttributeDefinition, ObjectDefinition
from ce1sus.db.classes.internal.event import Event, Comment
from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.classes.internal.report import ReferenceDefinition, Report
from ce1sus.db.classes.internal.usrmgt.group import Group
from ce1sus.db.classes.internal.usrmgt.user import User
from ce1sus.db.classes.internal.backend.mailtemplate import MailTemplate


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Assembler(BaseChangeController):

  def __init__(self, config, session=None):
    super(BaseChangeController, self).__init__(config, session)
    self.stix_assembler = StixAssembler(config, session)
    self.cybox_assembler = CyboxAssembler(config, session)
    self.ce1sus_assembler = Ce1susAssembler(config, session)
    self.event_assembler = EventAssembler(config, session)

  def assemble(self, json, clazz, parent, cache_object):

    cache_object.insert = True

    classname = clazz.get_classname()

    self.logger.debug('Assembling {0}'.format(classname))
    if classname == User.get_classname():
      return self.ce1sus_assembler.assemble_user(json, cache_object)
    elif classname == Group.get_classname():
      return self.ce1sus_assembler.assemble_group(json, cache_object)
    elif classname == SyncServer.get_classname():
      return self.ce1sus_assembler.assemble_serversync(json, cache_object)
    elif classname == AttributeDefinition.get_classname():
      return self.ce1sus_assembler.assemble_attribute_definition(json, cache_object)
    elif classname == ReferenceDefinition.get_classname():
      return self.ce1sus_assembler.assemble_reference_definition(json, cache_object)
    elif classname == Condition.get_classname():
      return self.ce1sus_assembler.assemble_condition_definition(json, cache_object)
    elif classname == ObjectDefinition.get_classname():
      return self.ce1sus_assembler.assemble_object_definition(json, cache_object)
    elif classname == AttributeType.get_classname():
      return self.ce1sus_assembler.assemble_attribute_type(json, cache_object)
    elif classname == MailTemplate.get_classname():
      return self.ce1sus_assembler.assemble_mail_template(json, cache_object)

    elif classname == Event.get_classname():
      return self.event_assembler.assemble_event(json, cache_object)
    elif classname == Comment.get_classname():
      return self.event_assembler.assemble_comment(parent, json, cache_object)
    elif classname == Observable.get_classname():
      return self.cybox_assembler.assemble_observable(parent, json, cache_object)
    elif classname == Object.get_classname():
      return self.cybox_assembler.assemble_object(parent, json, cache_object)
    elif classname == RelatedObject.get_classname():
      return self.cybox_assembler.assemble_related_object(parent, json, cache_object)
    elif classname == Report.get_classname():
      return self.event_assembler.assemble_report(parent, json, cache_object, dict())
    else:
      raise AssertionError('Class "{0}" not defined'.format(classname))


