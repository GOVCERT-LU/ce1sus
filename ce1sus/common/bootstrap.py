# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 10, 2015
"""


from ce1sus.helpers.common.config import ConfigException
import cherrypy
import logging
import os

from ce1sus.views.web.adapters.ce1susadapter import Ce1susViewAdapter
from ce1sus.views.web.adapters.openiocadapter import OpenIOCAdapter
from ce1sus.views.web.adapters.stixadapter import STIXAdapter
from ce1sus.views.web.api.version2.depricated import DepricatedView
from ce1sus.views.web.api.version3.maincontroller import MainController
from ce1sus.views.web.api.version3.mispcontroller import MISPController
from ce1sus.views.web.common.decorators import check_auth
from ce1sus.views.web.frontend.index import IndexView
from ce1sus.views.web.frontend.menus import GuiMenus
from ce1sus.views.web.frontend.plugin import GuiPlugins


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

def my_log_traceback(severity=logging.CRITICAL):
  """Write the last error's headers and traceback to the cherrypy error log witih a CRITICAL severity."""
  from cherrypy import _cperror
  h = ["  %s: %s" % (k, v) for k, v in cherrypy.request.header_list]
  cherrypy.log('\nRequest Headers:\n' + '\n'.join(h) + '\n\n' + _cperror.format_exc(), "HTTP", severity=severity)


def bootstrap(config, cherrypy_cfg='/../../config/cherrypy.conf'):
  basePath = os.path.dirname(os.path.abspath(__file__))
  cherrypyConfigFile = basePath + cherrypy_cfg

  try:
    if os.path.isfile(cherrypyConfigFile):
      cherrypy.config.update(cherrypyConfigFile)
    else:
      raise ConfigException('Could not find config file ' + cherrypyConfigFile)
  except cherrypy._cperror as error:
    raise ConfigException(error)

  cherrypy.tree.mount(IndexView(config), '/')
  cherrypy.tree.mount(MainController(config), '/REST/0.3.0/')
  cherrypy.tree.mount(DepricatedView(config), '/REST/0.2.0/')
  cherrypy.tree.mount(GuiMenus(config), '/menus')
  cherrypy.tree.mount(GuiPlugins(config), '/plugins')

  cherrypy.tree.mount(MISPController(config), '/MISP')
  cherrypy.tree.mount(STIXAdapter(config), '/STIX/0.1')
  cherrypy.tree.mount(OpenIOCAdapter(config), '/OpenIOC/0.1')
  cherrypy.tree.mount(Ce1susViewAdapter(config), '/ce1sus/0.1')
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
    getattr(cherrypy.log.error_log, 'addHandler')(h)
  return config
