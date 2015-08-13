# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.updater.update.ccybox.ccybox import CyboxUpdater
from ce1sus.controllers.common.updater.update.cstix import StixUpdater
from ce1sus.controllers.common.updater.update.internal.event import EventUpdater
from ce1sus.controllers.common.updater.update.internal.internal import Ce1susUpdater
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

class Updater(BaseController):

  def __init__(self, config, session=None):
    super(Updater, self).__init__(config, session)
    self.stix_updater = StixUpdater(config, session)
    self.cybox_updater = CyboxUpdater(config, session)
    self.ce1sus_updater = Ce1susUpdater(config, session)
    self.event_updater = EventUpdater(config, session)

  def update(self, instance, json, cache_object):
    cache_object.insert = False
    classname = instance.get_classname()
    self.logger.debug('Updating {0}'.format(classname))
    if classname == User.get_classname():
      return self.ce1sus_updater.update_user(instance, json, cache_object)
    elif classname == Group.get_classname():
      return self.ce1sus_updater.update_group(instance, json, cache_object)
    elif classname == SyncServer.get_classname():
      return self.ce1sus_updater.update_serversync(instance, json, cache_object)
    elif classname == AttributeDefinition.get_classname():
      return self.ce1sus_updater.update_attribute_definition(instance, json, cache_object)
    elif classname == AttributeType.get_classname():
      return self.ce1sus_updater.update_attribute_type(instance, json, cache_object)
    elif classname == MailTemplate.get_classname():
      return self.ce1sus_updater.update_mail_template(instance, json, cache_object)

    elif classname == ReferenceDefinition.get_classname():
      return self.ce1sus_updater.update_reference_definition(instance, json, cache_object)
    elif classname == Condition.get_classname():
      return self.ce1sus_updater.update_condition_definition(instance, json, cache_object)
    elif classname == ObjectDefinition.get_classname():
      return self.ce1sus_updater.update_object_definition(instance, json, cache_object)
    elif classname == Event.get_classname():
      return self.event_updater.update_event(instance, json, cache_object)
    elif classname == Comment.get_classname():
      return self.event_updater.update_comment(instance, json, cache_object)
    elif classname == Observable.get_classname():
      return self.cybox_updater.update_observable(instance, json, cache_object)
    elif classname == Object.get_classname():
      return self.cybox_updater.update_object(instance, json, cache_object)
    elif classname == RelatedObject.get_classname():
      return self.cybox_updater.update_related_object(instance, json, cache_object)
    elif classname == Report.get_classname():
      return self.event_updater.update_report(instance, json, cache_object)
    else:
      raise AssertionError('Class "{0}" not defined'.format(classname))
