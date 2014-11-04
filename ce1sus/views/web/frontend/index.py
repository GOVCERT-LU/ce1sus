# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import cherrypy
import json
import os
from os.path import exists

from ce1sus.common.system import APP_REL, DB_REL, REST_REL
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.common import create_response


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IndexView(BaseView):

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    # only for fetching the first page
    return open(os.path.join(cherrypy.config.get("tools.staticdir.root"), u'index.html'))

  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  @cherrypy.tools.json_out()
  def welcome_message(self):
    if self.user_authenticated():
      changelog_file = 'CHANGELOG'
      if exists(changelog_file):
        file_obj = open(changelog_file, 'r')
        result = ""
        counter = 0
        for line in file_obj:
          if 'Release' in line:
            counter = counter + 1
          if counter == 2:
            break
          if counter > 0:
            result = u'{0}\n{1}'.format(result, line)

        return create_response(result)
      else:
        return create_response('No new messages')
    else:
      return create_response('Login')
