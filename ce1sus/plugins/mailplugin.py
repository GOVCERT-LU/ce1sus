# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 7, 2014
"""
from ce1sus.helpers.common.mailer import Mailer, Mail, MailerException
from ce1sus.plugins.base import BasePlugin, plugin_internal_method, PluginException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailPlugin(BasePlugin):

  def __init__(self, config):
    super(BasePlugin, self).__init__(config)
    self.mailer = Mailer(config)

  @plugin_internal_method
  def create_mail(self, subject, reciever, body, encrypt=True):
    mail = Mail()
    mail.subject = subject
    # if set to none the default sender is taken
    mail.sender = None
    mail.body = body
    mail.reciever = reciever
    mail.encrypt = encrypt

  @plugin_internal_method
  def send_mail(self, mail):
    try:
      self.mailer.send_mail(mail)
    except MailerException as error:
      raise PluginException(error)

  @plugin_internal_method
  def import_gpg_key(self, gpg_key):
    self.mailer.import_gpg(gpg_key)

  @plugin_internal_method
  def get_instance(self):
    return self
