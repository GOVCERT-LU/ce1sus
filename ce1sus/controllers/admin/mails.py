# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.mailtemplate import MailTemplateBroker
from ce1sus.db.common.broker import BrokerException, ValidationException, NothingFoundException
from ce1sus.helpers.common.mailer import Mail
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailController(BaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.mail_broker = self.broker_factory(MailTemplateBroker)
    self.mail_handler = None
    if is_plugin_available('mail', self.config):
      self.mail_handler = get_plugin_function('mail', 'get_instance', self.config, 'internal_plugin')()

  def get_all(self):
    try:
      return self.mail_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_by_id(self, mail_id):
    try:
      return self.mail_broker.get_by_id(mail_id)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def get_by_uuid(self, uuid):
    try:
      return self.mail_broker.get_by_uuid(uuid)
    except NothingFoundException as error:
      raise ControllerNothingFoundException(error)
    except BrokerException as error:
      raise ControllerException(error)

  def update_mail(self, mail_template, user):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_simple_logging(mail_template, user, insert=False)
      mail_template = self.mail_broker.update(mail_template)
      return mail_template
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(mail_template)
      raise ControllerException(u'Could not update mail due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def insert_mail(self, mail_template, user, commit=True):
    try:
      user = self.user_broker.get_by_id(user.identifier)
      self.set_simple_logging(mail_template, user, insert=False)
      mail_template = self.mail_broker.insert(mail_template, False)
      self.mail_broker.do_commit(commit)
      return mail_template
    except ValidationException as error:
      message = ObjectValidator.getFirstValidationError(mail_template)
      raise ControllerException(u'Could not insert mail due to: {0}'.format(message))
    except BrokerException as error:
      raise ControllerException(error)

  def import_gpg_key(self, key):
    if self.mail_handler:
      self.mail_handler.import_gpg_key(key)

  def send_activation_mail(self, user):
    try:
      if self.mail_handler:
        mail_tmpl = self.mail_broker.get_activation_template()
        mail = Mail()
        mail.reciever = user.email
        mail.subject = mail_tmpl.subject
        body = mail_tmpl.body
        url = self.config.get('ce1sus', 'baseurl')
        activation_url = url + u'/#/activate/{0}'.format(user.activation_str)
        body = body.replace(u'${name}', u'{0}'.format(user.name))
        body = body.replace(u'${sirname}', u'{0}'.format(user.sirname))
        body = body.replace(u'${username}', u'{0}'.format(user.username))
        body = body.replace(u'${password}', u'{0}'.format(user.plain_password))
        body = body.replace(u'${ce1sus_url}', u'{0}'.format(url))
        body = body.replace(u'${activation_link}', u'{0}'.format(activation_url))
        mail.body = body

        if user.gpg_key:
          mail.encrypt = True

        self.mail_handler.send_mail(mail)
    except Exception as error:
      self.user_broker.update(user)
      self.logger.info(u'Could not send activation email to "{0}" for user "{1}" Error:{2}'.format(user.email, user.username, error))
      raise ControllerException(u'Could not send activation email to "{0}" for user "{1}"'.format(user.email, user.username))
