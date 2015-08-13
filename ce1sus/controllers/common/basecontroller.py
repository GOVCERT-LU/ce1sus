# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.events.event import EventController
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.report import Report, Reference


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class BaseChangeControllerException(ControllerException):
  pass


class BaseChangeController(BaseController):

  def __init__(self, config, session):
    super(BaseController, self).__init__(config, session)
    self.event_controller = EventController(config, session)

  def __get_event(self, instance):
    if isinstance(instance, Event):
      return instance
    elif isinstance(instance, Observable):
      if instance.event:
        return instance.event
      else:
        # for observables in indicators
        return instance.parent.event
    elif isinstance(instance, Object):
      return instance.event
    elif isinstance(instance, Attribute):
      return instance.object.event
    elif isinstance(instance, Report):
      return instance.event
    elif isinstance(instance, Reference):
      return instance.report.event
    else:
      raise BaseChangeControllerException('Getting Event for {0} is not defined'.format(instance.get_classname()))
