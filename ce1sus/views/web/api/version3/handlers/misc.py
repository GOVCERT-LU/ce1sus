# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
from ce1sus.common.system import APP_REL, DB_REL, REST_REL
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods
from ce1sus.views.web.common.common import create_response


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class VersionHandler(RestBaseHandler):

  @rest_method(default=True)
  @methods(allowed=['GET'])
  def version(self, **args):
    result = dict()
    result['application'] = APP_REL
    result['dataBase'] = DB_REL
    result['restApi'] = REST_REL
    return create_response(result)
