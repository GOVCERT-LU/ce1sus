# -*- coding: utf-8 -*-

"""
module handing the the administrative index pages

Created on July 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged, requireReferer


class AdminController(Ce1susBaseController):
  """admim controller handling all actions in the admin section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/adminBase.html')
    self.setAdminArea(True)
    return self.cleanHTMLCode(template.render())
