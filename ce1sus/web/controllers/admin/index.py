"""module holding all controllers needed for the administration"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# Created on July 26, 2013

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
    index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/adminBase.html')
    return template.render()
