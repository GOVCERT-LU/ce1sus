# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView
from ce1sus.controllers.login import LoginController, ActivationTimedOut
import cherrypy
from cherrypy._cperror import HTTPRedirect
from ce1sus.web.views.common.decorators import require
from dagr.helpers.validator.valuevalidator import ValueValidator
from dagr.controllers.base import ControllerException


class IndexView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.login_controller = LoginController(config)

  def __get_environment_string(self):
    """
    Returns the string for displaying the environment
    """
    env = self._get_config_variable('environment', 'Item environment is not specified in the configuration.')
    env = '[{0}]'.format(env)
    return env

  @cherrypy.expose
  def index(self, error_msg=None):
    """
    The index page of ce1sus. Mainly only an login page

    :param errorMsg: Error message to be displayed
    :type errorMsg: String

    :returns: generated HTML
    """
    user = self._get_user()
    if user:
      return self.internal()
    return self.login(error_msg)

  @cherrypy.expose
  def login(self, error_msg=None):
    """
    Renders the login Page

    :returns: generated HTML
    """
    # self.destroy_session()
    self.set_admin_area(False)

    return self._render_template('/index/login.html',
                                 error_msg=error_msg,
                                 env=self.__get_environment_string(),
                                 is_authenticated=False)

  @cherrypy.expose
  def dologin(self, username=None, password=None):
    """
    Login of the page. This function checks if the credentials are valid and
    if so sets a session for the user. Also redirects the user to the index
    page of the internal site.

    :param username: the username
    :type username: String
    :param password: the password of the user (paintext?)
    :type password: String

    """
    try:
      if username is None or password is None:
        raise HTTPRedirect('/index')
        # validate user and user name
      if  (not ValueValidator.validateAlNum(username, minLength=1, maxLength=64, withSymbols=True, withSpaces=True) and
           not ValueValidator.validateAlNum(password, minLength=1, maxLength=64, withSymbols=True, withSpaces=True)):
        return self.index('Invalid input.')
      user = self.login_controller.get_user_by_usr_pwd(username, password)
      self.login_controller.update_last_login(user)
      # put in session
      self._put_user_to_session(user)
      self._get_logger().info('User "{0}" logged in'.format(user.username))
      raise HTTPRedirect('/internal')
    except ControllerException:
      return self.index('Invalid username or password.')

  @cherrypy.expose
  @require()
  def logout(self):
    """
    Log out method
    """
    self._get_logger().info('User {0} logged out'.format(self._get_user().username))
    self._destroy_session()
    raise HTTPRedirect('/')

  @require()
  @cherrypy.expose
  def internal(self):
    """
    Renders the base for the whole page in the internal section

    :returns: generated HTML
    """

    return self._render_template('/index/basePage.html',
                                 env=self.__get_environment_string(),
                                 is_authenticated=True)

  @cherrypy.expose
  def activate(self, activation_str=None):
    try:
      if activation_str:
        self.login_controller.activate_user(activation_str)
        return self._render_template('/index/authenticate.html',
                                   env=self.__get_environment_string(),
                                   error_msg=None)
      raise HTTPRedirect('/')
    except ActivationTimedOut as error:
      return self._render_template('/index/authenticate.html',
                                   env=self.__get_environment_string(),
                                   error_msg=error.message)
    except ControllerException:
      raise HTTPRedirect('/')
