# -*- coding: utf-8 -*-

"""
(Description)

Created on Mar 19, 2015
"""
import cherrypy

from ce1sus.views.web.common.base import BaseView


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DepricatedView(BaseView):

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST', 'PUT', 'DELETE'])
    def index(self):
        raise cherrypy.HTTPError(status=410, message='The interface for version 0.2.0 is depricated use 0.3.0 instead')
