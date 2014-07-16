# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 15, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
import cherrypy
from ce1sus.web.views.helpers.tabs import MainTab, EventTab, AdminTab, ValidationTab
from ce1sus.common.system import put_to_array


class ViewHandler(object):

  def __init__(self):
    # lvl 0 tabs
    self.main_tabs = list()
    # lvl 1 tabs
    self.event_tabs = list()
    self.admin_tabs = list()
    self.validation_tabs = list()
    self.tree = cherrypy.tree

  def add_view(self, view, url):
    tabs = view.tabs()
    if tabs:
      for tab in tabs:
        if isinstance(tab, MainTab):
          put_to_array(self.main_tabs, tab.position, tab)
        if isinstance(tab, EventTab):
          put_to_array(self.event_tabs, tab.position, tab)
        if isinstance(tab, AdminTab):
          put_to_array(self.admin_tabs, tab.position, tab)
        if isinstance(tab, ValidationTab):
          put_to_array(self.validation_tabs, tab.position, tab)
    view.view_handler = self
    self.tree.mount(view, url)
