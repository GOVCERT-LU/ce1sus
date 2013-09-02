# -*- coding: utf-8 -*-

"""
module handing the the administrative index pages

Created on July 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged

class AdminController(BaseController):
  """admim controller handling all actions in the admin section"""

  def __init__(self):
    BaseController.__init__(self)

  @cherrypy.expose
  @require(privileged())
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/adminBase.html')
    return template.render()
