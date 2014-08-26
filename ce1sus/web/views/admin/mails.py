# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.views.base import Ce1susBaseView, privileged
from ce1sus.controllers.admin.mails import MailController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException
from ce1sus.web.views.helpers.tabs import AdminTab


class AdminMailView(Ce1susBaseView):

  ID = 'Mail'

  def tabs(self):
    mail_tab = AdminTab(title='Mail Templates',
                        url='/admin/mails',
                        options='reload',
                        position=6)
    return [mail_tab]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.mail_controller = MailController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/common/adminSubItemBase.html',
                                 id=AdminMailView.ID,
                                 url_left_content='/admin/mails/left_content')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def left_content(self):
    try:
      mail_templates = self.mail_controller.get_all()
      return self._render_template('/admin/mails/leftContent.html',
                                   id=AdminMailView.ID,
                                   url_right_content='/admin/mails/right_content',
                                   action_url='/admin/mails/modify_mail',
                                   refresh_url='/admin/mails',
                                   modal_content_url='/admin/mails/add_mails',
                                   items=mail_templates)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def right_content(self, mail_id):
    try:
      mail_template = self.mail_controller.get_by_id(mail_id)
      return self._render_template('/admin/mails/rightContent.html',
                                   mail_template=mail_template)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_mail(self, mail_id):
    try:
      mail_template = self.mail_controller.get_by_id(mail_id)
      return self._render_template('/admin/mails/mailModal.html',
                                   mail_template=mail_template)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def modify_mail(self, identifier=None, subject=None,
                  body=None, action='insert'):
    try:
      self._check_if_valid_action(action)
      if action == 'update':
        user = self._get_user()
        mail_template = self.mail_controller.get_by_id(identifier)
        mail_template.subject = subject
        mail_template.body = body
        mail_template, valid = self.mail_controller.update_mail(user, mail_template)
        if not valid:
            self._get_logger().info('Event is invalid')
            return self._return_ajax_post_error(self._render_template('/admin/mails/mailModal.html',
                                                                      mail_template=mail_template))
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)
