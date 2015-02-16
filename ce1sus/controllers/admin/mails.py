# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""
from ce1sus.controllers.base import BaseController, ControllerException, ControllerNothingFoundException
from ce1sus.db.brokers.mailtemplate import MailTemplateBroker
from ce1sus.db.common.broker import BrokerException, ValidationException, NothingFoundException
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailController(BaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.mail_broker = self.broker_factory(MailTemplateBroker)

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
