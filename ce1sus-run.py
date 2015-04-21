# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import cherrypy
import os
import sys
import logging

from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.object import Object
from ce1sus.helpers.common.config import Configuration
from ce1sus.views.web.api.version2.depricated import DepricatedView
from ce1sus.views.web.api.version3.restcontroller import RestController
from ce1sus.views.web.common.decorators import check_auth
from ce1sus.views.web.frontend.index import IndexView
from ce1sus.views.web.frontend.menus import GuiMenus
from ce1sus.views.web.frontend.plugin import GuiPlugins
from ce1sus.views.web.adapters.misp.misp import MISPAdapter


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def my_log_traceback(severity=logging.CRITICAL):
    """Write the last error's headers and traceback to the cherrypy error log witih a CRITICAL severity."""
    from cherrypy import _cperror
    h = ["  %s: %s" % (k, v) for k, v in cherrypy.request.header_list]
    cherrypy.log('\nRequest Headers:\n' + '\n'.join(h) + '\n\n' + _cperror.format_exc(), "HTTP", severity=severity)


def bootstrap():
  basePath = os.path.dirname(os.path.abspath(__file__))
  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  cherrypyConfigFile = basePath + '/config/cherrypy.conf'

  try:
    if os.path.isfile(cherrypyConfigFile):
      cherrypy.config.update(cherrypyConfigFile)
    else:
      raise ConfigException('Could not find config file ' + cherrypyConfigFile)
  except cherrypy._cperror as error:
    raise ConfigException(error)

  # load configuration file
  config = Configuration(ce1susConfigFile)

  cherrypy.tree.mount(IndexView(config), '/')
  cherrypy.tree.mount(RestController(config), '/REST/0.3.0/')
  cherrypy.tree.mount(DepricatedView(config), '/REST/0.2.0/')
  cherrypy.tree.mount(GuiMenus(config), '/menus')
  cherrypy.tree.mount(GuiPlugins(config), '/plugins')

  cherrypy.tree.mount(MISPAdapter(config), '/MISP/0.1')

  # instantiate auth module
  cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

  cherrypy.tools.my_log_tracebacks = cherrypy.Tool('before_error_response', my_log_traceback)

  use_mailer = config.get('ErrorMails', 'enabled', False)
  if use_mailer:
    smtpserver = config.get('ErrorMails', 'smtp')
    fromaddr = config.get('ErrorMails', 'sender')
    toaddr = config.get('ErrorMails', 'receiver')
    subject = config.get('ErrorMails', 'subject')
    h = logging.handlers.SMTPHandler(smtpserver, fromaddr, toaddr, subject)
    log_lvl = getattr(logging, config.get('ErrorMails', 'level', 'error').upper())
    h.setLevel(log_lvl)
    cherrypy.log.error_log.addHandler(h)

if __name__ == '__main__':

  bootstrap()
  try:
    cherrypy.engine.start()
    cherrypy.engine.block()
  except cherrypy._cperror as e:
    raise ConfigException(e)
else:
  bootstrap()
  cherrypy.engine.start()
  application = cherrypy.tree
