# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 23, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import BrokerException, ValidationException, IntegrityException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.groupbroker import GroupBroker
from ce1sus.brokers.permission.permissionclasses import Group
from dagr.controllers.base import ControllerException
from dagr.helpers.mailer import Mailer, Mail, MailerException
from ce1sus.brokers.mailbroker import MailTemplateBroker


class MailController(Ce1susBaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.mail_broker = self.broker_factory(MailTemplateBroker)

  def get_all(self):
    try:
      return self.mail_broker.get_all()
    except BrokerException as error:
      self._get_logger().error(error)

  def get_by_id(self, mail_id):
    try:
      return self.mail_broker.get_by_id(mail_id)
    except BrokerException as error:
      self._get_logger().error(error)

  def update_mail(self, user, mail_template):
    try:
      mail_template = self.mail_broker.update(mail_template)
      return mail_template, True
    except ValidationException as error:
      return mail_template, False
    except BrokerException as error:
      self._raise_exception(error)
