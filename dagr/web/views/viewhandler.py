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
      works = False
      for tab in tabs:
        if tab:
          name = tab[0]
          lvl = tab[1]
          link_url = tab[2]
          button_type = tab[3]
          if lvl == 0:
            self.main_tabs.append((name, link_url, button_type))
          if lvl == 1:
            self.event_tabs.append((name, link_url, button_type))
          if lvl == -1:
            self.admin_tabs.append((name, link_url, button_type))
          if lvl == -2:
            self.validation_tabs.append((name, link_url, button_type))
    view.view_handler = self

    self.tree.mount(view, url)
