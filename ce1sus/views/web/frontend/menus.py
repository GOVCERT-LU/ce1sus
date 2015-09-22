# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 24, 2014
"""
import cherrypy

from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GuiMenus(BaseView):

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  @cherrypy.tools.json_out()
  def primary_menus(self):
    user = self.get_user()
    menus = list()
    if self.user_authenticated():
      menu_item = dict()
      menu_item['icon'] = 'fa-home'
      menu_item['title'] = 'Home'
      menu_item['section'] = 'main.layout.home'
      menus.append(menu_item)

      menu_item = dict()
      menu_item['icon'] = 'fa-database'
      menu_item['title'] = 'Events'
      menu_item['section'] = 'main.layout.events'
      menu_item['submenus'] = None
      menus.append(menu_item)

      # Todo if user can access admin area show it else not
      if user.permissions.access_admin_area:
        menu_item = dict()
        menu_item['icon'] = 'fa-cog'
        menu_item['title'] = 'Administration'

        child_menus = list()

        if user.permissions.validate:
          child_menu_item = dict()
          child_menu_item['title'] = 'Validate events'
          child_menu_item['section'] = 'admin/validation'
          child_menus.append(child_menu_item)

          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        attributemgt = False
        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Objects'
          child_menu_item['section'] = 'admin/object'
          child_menus.append(child_menu_item)
          attributemgt = True

        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Attributes'
          child_menu_item['section'] = 'admin/attribute'
          child_menus.append(child_menu_item)
          attributemgt = True

        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Conditions'
          child_menu_item['section'] = 'admin/condition'
          child_menus.append(child_menu_item)
          attributemgt = True

        if attributemgt:
          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        attributeSubTypemgt = False

        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Types'
          child_menu_item['section'] = 'admin/type'
          child_menus.append(child_menu_item)
          attributeSubTypemgt = True

        if attributeSubTypemgt:
          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        referencesmgt = False

        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'References'
          child_menu_item['section'] = 'admin/reference'
          child_menus.append(child_menu_item)
          referencesmgt = True

        if referencesmgt:
          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        syncserver = False

        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Sync Servers'
          child_menu_item['section'] = 'admin/syncservers'
          child_menus.append(child_menu_item)
          syncserver = True

        if syncserver:
          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        bg_jobs = False
        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Background Jobs'
          child_menu_item['section'] = 'admin/jobs'
          child_menus.append(child_menu_item)
          bg_jobs = True

        if bg_jobs:
          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        usermgt = False
        if user.permissions.privileged:
          usermgt = True
          child_menu_item = dict()
          child_menu_item['title'] = 'Users'
          child_menu_item['section'] = 'admin/user'
          child_menus.append(child_menu_item)

        if user.permissions.privileged:
          usermgt = True
          child_menu_item = dict()
          child_menu_item['title'] = 'Groups'
          child_menu_item['section'] = 'admin/group'
          child_menus.append(child_menu_item)

        if usermgt:
          child_menu_item = dict()
          child_menu_item['divider'] = True
          child_menus.append(child_menu_item)

        if user.permissions.privileged:
          child_menu_item = dict()
          child_menu_item['title'] = 'Mails'
          child_menu_item['section'] = 'admin/mail'
          child_menus.append(child_menu_item)

        if child_menus:
          menu_item['submenus'] = child_menus
          menus.append(menu_item)

      menu_item = dict()
      menu_item['icon'] = 'fa-user'
      menu_item['title'] = 'User'

      child_menus = list()

      child_menu_item = dict()
      child_menu_item['title'] = 'Profile'
      child_menu_item['section'] = 'user/profile'
      child_menus.append(child_menu_item)

      if user.permissions.manage_group:
        child_menu_item = dict()
        child_menu_item['divider'] = True
        child_menus.append(child_menu_item)

        child_menu_item = dict()
        child_menu_item['title'] = 'Group Mgt'
        child_menu_item['section'] = 'user/group'
        child_menus.append(child_menu_item)

      menu_item['submenus'] = child_menus

      menus.append(menu_item)

      menu_item = dict()
      menu_item['icon'] = 'fa-question'
      menu_item['title'] = 'Help'

      child_menus = list()
      child_menu_item = dict()
      child_menu_item['title'] = 'Rest API'
      child_menu_item['section'] = '/help/restapi'
      child_menus.append(child_menu_item)

      child_menu_item = dict()
      child_menu_item['divider'] = True
      child_menus.append(child_menu_item)

      child_menu_item = dict()
      child_menu_item['title'] = 'About'
      child_menu_item['section'] = '/help/about'
      child_menus.append(child_menu_item)

      menu_item['submenus'] = child_menus
      menus.append(menu_item)

      menu_item = dict()
      menu_item['icon'] = 'fa-lock'
      menu_item['title'] = 'Logout'
      menu_item['section'] = 'main.layout.logout'
      menus.append(menu_item)

    else:
      menu_item = dict()
      menu_item['icon'] = 'fa-home'
      menu_item['title'] = 'Home'
      menu_item['section'] = 'main.layout.home'
      menus.append(menu_item)

      menu_item = dict()
      menu_item['icon'] = 'fa-unlock'
      menu_item['title'] = 'Login'
      menu_item['section'] = 'main.layout.login'
      menus.append(menu_item)

      menu_item = dict()
      menu_item['icon'] = 'fa-question'
      menu_item['title'] = 'Help'

      # Note: chind menu's section is the actual link
      child_menus = list()
      child_menu_item = dict()
      child_menu_item['title'] = 'About'
      child_menu_item['section'] = '/about'
      child_menus.append(child_menu_item)
      menu_item['submenus'] = child_menus
      menus.append(menu_item)

    return menus

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  @cherrypy.tools.json_out()
  @require()
  def event_links(self):
    # links on the left side of the events menu
    links = list()

    link_item = dict()
    link_item['icon'] = 'fa-database'
    link_item['title'] = 'All Events'
    link_item['section'] = 'main.layout.events.allEvents'
    link_item['reload'] = False
    link_item['href'] = link_item['section']
    links.append(link_item)

    """
    link_item = dict()
    link_item['title'] = 'Unpublished'
    link_item['section'] = 'main.layout.events.unpublished'
    link_item['reload'] = False
    link_item['href'] = link_item['section']
    links.append(link_item)
    link_item = dict()
    """

    link_item = dict()
    link_item['icon'] = 'fa-search'
    link_item['title'] = 'Search Attribtues'
    link_item['section'] = 'main.layout.events.serach'
    link_item['href'] = link_item['section']
    links.append(link_item)

    link_item = dict()
    link_item['icon'] = 'fa-plus'
    link_item['title'] = 'Add Event'
    link_item['section'] = 'main.layout.events.add'
    link_item['href'] = link_item['section']
    links.append(link_item)
    return links
