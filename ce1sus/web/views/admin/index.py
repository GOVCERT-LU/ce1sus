# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 3, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView, privileged
from ce1sus.controllers.event.groups import GroupsController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class AdminView(Ce1susBaseView):
  """index view handling all display in the index section"""
  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)

  def tabs(self):
    return None

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    tabs = list()
    if self.view_handler:
      tabs = self.view_handler.admin_tabs
    return self._render_template('/admin/adminBase.html',
                                 tabs=tabs)
