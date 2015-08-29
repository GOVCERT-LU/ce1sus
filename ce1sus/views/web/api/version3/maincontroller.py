# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 26, 2015
"""

from ce1sus.views.web.api.version3.base import AbstractRestController
from ce1sus.views.web.api.version3.handlers.admin.adminattributehandler import AdminAttributeHandler
from ce1sus.views.web.api.version3.handlers.admin.admingrouphandler import AdminGroupHandler
from ce1sus.views.web.api.version3.handlers.admin.adminindicatorhandler import AdminIndicatorTypesHandler
from ce1sus.views.web.api.version3.handlers.admin.adminobjecthandler import AdminObjectHandler
from ce1sus.views.web.api.version3.handlers.admin.adminreferencehandler import AdminReferenceDefinitionHandler
from ce1sus.views.web.api.version3.handlers.admin.admintypehandler import AttribueTypeHandler
from ce1sus.views.web.api.version3.handlers.admin.adminuserhandler import AdminUserHandler
from ce1sus.views.web.api.version3.handlers.admin.adminvalidationhandler import ValidationHandler
from ce1sus.views.web.api.version3.handlers.admin.conditionhandler import ConditionHandler
from ce1sus.views.web.api.version3.handlers.admin.mailhandler import MailHandler
from ce1sus.views.web.api.version3.handlers.admin.syncservershandler import SyncServerHandler
from ce1sus.views.web.api.version3.handlers.common.definitions import StatusHandler, AnalysisHandler, RiskHandler, TLPHanlder, RelationHandler
from ce1sus.views.web.api.version3.handlers.common.grouphandler import GroupHandler
from ce1sus.views.web.api.version3.handlers.common.processhandler import ProcessHandler
from ce1sus.views.web.api.version3.handlers.common.restchecks import ChecksHandler
from ce1sus.views.web.api.version3.handlers.events.eventhandler import EventHandler
from ce1sus.views.web.api.version3.handlers.events.eventshandler import EventsHandler
from ce1sus.views.web.api.version3.handlers.events.objecthandler import ObjectHandler
from ce1sus.views.web.api.version3.handlers.events.observablehanlder import ObservableHandler
from ce1sus.views.web.api.version3.handlers.events.reporthandler import ReportHandler
from ce1sus.views.web.api.version3.handlers.events.searchhandler import SearchHandler
from ce1sus.views.web.api.version3.handlers.loginhandler import LoginHandler, LogoutHandler
from ce1sus.views.web.api.version3.handlers.mischandler import VersionHandler, HandlerHandler, TablesHandler, ReferenceHandlerHandler, SyncServerTypesHandler, \
  UserGroupsHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class MainController(AbstractRestController):

  def set_instances(self, config):
    self.instances['login'] = LoginHandler(config)
    self.instances['logout'] = LogoutHandler(config)
    self.instances['version'] = VersionHandler(config)
    self.instances['user'] = AdminUserHandler(config)
    self.instances['group'] = AdminGroupHandler(config)
    self.instances['mail'] = MailHandler(config)
    self.instances['objectdefinition'] = AdminObjectHandler(config)
    self.instances['attributedefinition'] = AdminAttributeHandler(config)
    self.instances['attributehandlers'] = HandlerHandler(config)
    self.instances['attributetables'] = TablesHandler(config)
    self.instances['attributetypes'] = AttribueTypeHandler(config)
    self.instances['event'] = EventHandler(config)
    self.instances['observable'] = ObservableHandler(config)
    self.instances['object'] = ObjectHandler(config)
    self.instances['events'] = EventsHandler(config)
    self.instances['statuses'] = StatusHandler(config)
    self.instances['analyses'] = AnalysisHandler(config)
    self.instances['risks'] = RiskHandler(config)
    self.instances['tlps'] = TLPHanlder(config)
    self.instances['checks'] = ChecksHandler(config)
    self.instances['groups'] = GroupHandler(config)
    self.instances['relations'] = RelationHandler(config)
    self.instances['condition'] = ConditionHandler(config)
    self.instances['validate'] = ValidationHandler(config)
    self.instances['search'] = SearchHandler(config)
    self.instances['referencehandlers'] = ReferenceHandlerHandler(config)
    self.instances['referencedefinition'] = AdminReferenceDefinitionHandler(config)
    self.instances['report'] = ReportHandler(config)
    self.instances['indicatortypes'] = AdminIndicatorTypesHandler(config)
    self.instances['syncservers'] = SyncServerHandler(config)
    self.instances['servertypes'] = SyncServerTypesHandler(config)
    self.instances['tlps'] = TLPHanlder(config)
    self.instances['processes'] = ProcessHandler(config)
    self.instances['usergroups'] = UserGroupsHandler(config)
