# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import cherrypy

from ce1sus.helpers.common.objects import get_methods
from ce1sus.views.web.api.version3.handlers.admin.adminattributehandler import AdminAttributeHandler
from ce1sus.views.web.api.version3.handlers.admin.admingrouphandler import AdminGroupHandler
from ce1sus.views.web.api.version3.handlers.admin.adminobjecthandler import AdminObjectHandler
from ce1sus.views.web.api.version3.handlers.admin.admintypehandler import AttribueTypeHandler
from ce1sus.views.web.api.version3.handlers.admin.adminuserhandler import AdminUserHandler
from ce1sus.views.web.api.version3.handlers.admin.adminviewtypehandler import AttribueViewTypeHandler
from ce1sus.views.web.api.version3.handlers.admin.mailhandler import MailHandler
from ce1sus.views.web.api.version3.handlers.loginhandler import LoginHandler, LogoutHandler
from ce1sus.views.web.api.version3.handlers.mischandler import VersionHandler, HandlerHandler, TablesHandler
from ce1sus.views.web.api.version3.handlers.restbase import RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import SESSION_KEY


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RestController(BaseView):

  def __init__(self, config):
    BaseView.__init__(self, config)
    self.instances = dict()
    # add instances known to rest and their first URL
    self.instances['login'] = LoginHandler(config)
    self.instances['logout'] = LogoutHandler(config)
    self.instances['version'] = VersionHandler(config)
    self.instances['user'] = AdminUserHandler(config)
    self.instances['group'] = AdminGroupHandler(config)
    self.instances['mail'] = MailHandler(config)
    self.instances['object'] = AdminObjectHandler(config)
    self.instances['attribute'] = AdminAttributeHandler(config)
    self.instances['attributehandlers'] = HandlerHandler(config)
    self.instances['attributetables'] = TablesHandler(config)
    self.instances['attributetypes'] = AttribueTypeHandler(config)
    self.instances['attribtueviewtypes'] = AttribueViewTypeHandler(config)

  @staticmethod
  def find_default_method_name(instance):
    methods = get_methods(instance)
    for method in methods:
      function = getattr(instance, method)
      if hasattr(function, 'default_fct'):
        return method
    return None

  def __check_requirements(self, conditions):
    # requested_address = urllib.quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
      session = getattr(cherrypy, 'session')
      username = session.get(SESSION_KEY, None)
      if username:
        cherrypy.request.login = username
        for condition in conditions:
          # A condition is just a callable that returns true or false
          if not condition():
            # TODO: log why if possible
            raise cherrypy.HTTPError(403, 'No allowed')
        # TODO: redirect the user to the requested url if the url matches!! -> external view of an event
        # raise cherrypy.HTTPRedirect(requested_address)
      else:
        raise cherrypy.HTTPError(403, 'Not authenticated')

  @cherrypy.expose
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  @cherrypy.tools.allow(methods=['GET', 'PUT', 'POST', 'DELETE'])
  def default(self, *vpath, **params):
    try:
      path = list()
      handler = None
      # the first element in vpath is the name of the handler to use
      # the remaining elements are the parameters for the handler
      first_element = True
      for node in vpath:
        if first_element:
          handler = node
          first_element = False
        else:
          path.append(node)

      if not handler:
        raise cherrypy.HTTPError('Root requests are not allowed')

      # get the requested handler
      handler_instance = self.instances.get(handler, None)

      if not handler_instance:
        raise cherrypy.HTTPError('Handler "{0}" is not defined'.format(handler))

      # get default access point of the handler
      method_name = RestController.find_default_method_name(handler_instance)

      if not method_name:
        raise cherrypy.HTTPError('Handler {0} has no default method'.format(handler_instance.name))

      http_method = cherrypy.request.method

      json = {}
      if hasattr(cherrypy.request, 'json'):
        json = cherrypy.request.json

      method = getattr(handler_instance, method_name, None)

      if hasattr(method, 'rest_method'):
        # check if the is has requriements
        if hasattr(method, 'require_auth_flag'):
          conditions = method.require_auth
          self.__check_requirements(conditions)

        # check if http_method is allowed on function
        if hasattr(method, 'allowed_http_methods'):
          if http_method in method.allowed_http_methods:
            try:
              headers = cherrypy.request.headers
              result = method(path=path, json=json, method=http_method, headers=headers, parameters=params)
              # execute method
              return result
            except RestHandlerException as error:
              if isinstance(error, RestHandlerNotFoundException):
                raise cherrypy.HTTPError(status=404, message=u'{0}'.format(error))
              raise cherrypy.HTTPError(status=400, message=u'{0}'.format(error))
          else:
            raise cherrypy.HTTPError(status=501, message='Handler {0} \'s fucntion {1} does not support the {2} method'.format(handler_instance.name, method_name, http_method))
        else:
          raise cherrypy.HTTPError(status=405, message='Handler {0} \'s fucntion {1} has no http methods specified'.format(handler_instance.name, method_name))

      else:
        raise cherrypy.HTTPError(status=418, message='Handler {0} \'s fucntion {1} is not a rest function'.format(handler_instance.name, method_name))
    except Exception as error:
      if self.config.get('ce1sus', 'environment', None) == 'LOCAL_DEV':
        raise
      else:
        raise cherrypy.HTTPError(status=400, message=u'{0}'.format(error))
