# -*- coding: utf-8 -*-

"""
module handing the search pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from ce1sus.web.helpers.protection import require
from ce1sus.web.helpers.protection import privileged

class SearchController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)

  @require(privileged())
  @cherrypy.expose
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    return self.__class__.__name__ + ' is not implemented'
