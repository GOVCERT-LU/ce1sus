# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import cherrypy
import string

from ce1sus.controllers.base import ControllerException
from ce1sus.controllers.login import LoginController
from ce1sus.db.classes.user import UserRights
from ce1sus.helpers.common.objects import GenObject
from ce1sus.helpers.common.validator.valuevalidator import ValueValidator
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require
from ce1sus.views.web.common.common import create_response
from ce1sus.views.web.common.decorators import SESSION_USER


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LoginHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.login_controller = LoginController(config)

  @rest_method(default=True)
  @methods(allowed=['POST'])
  def login(self, **args):
    try:
      credentials = args.get('json')
      if credentials:
        usr = credentials.get('usr', None)
        pwd = credentials.get('pwd', None)
        if usr and pwd:
          # check if input is valid:
          printable_chars = string.printable[:-5]
          regex = '[{0}]'.format(printable_chars) + '{1,64}'
          if (not ValueValidator.validateRegex(usr, regex, 'errorMsg')
             and
             not ValueValidator.validateRegex(pwd, regex, 'errorMsg')):
            raise ControllerException(u'Illegal input')
          user = self.login_controller.get_user_by_usr_pwd(usr, pwd)
          self.login_controller.update_last_login(user)
          # put in session
          self.__put_user_to_session(user)
          self.logger.info('User "{0}" logged in'.format(user.username))
      return create_response('User Logged in')
    except ControllerException as error:
      self.logger.info(error)
      return self.raise_exception(Exception('User or password are incorrect.'), False)

  def __put_user_to_session(self, user):
    cherrypy.request.login = user.username
    self._put_to_session('_cp_username', user.username)
    offline_user = self.__make_user_object(user)
    self._put_to_session(SESSION_USER, offline_user)

  def __make_user_object(self, user):
    # TODO: make user offline
    obj = GenObject()
    obj.name = user.name
    obj.username = user.username
    obj.identifier = user.identifier
    obj.email = user.email
    obj.group_id = user.group_id
    obj.activated = user.activated
    obj.sirname = user.sirname
    obj.permissions = UserRights(user.dbcode)

    return obj


class LogoutHandler(RestBaseHandler):

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def logout(self, **args):
    self._destroy_session()
    return create_response('User logged out')
