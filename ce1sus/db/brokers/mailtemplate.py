# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 21, 2014
"""


from ce1sus.db.classes.mailtemplate import MailTemplate
from ce1sus.db.common.broker import BrokerBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailTemplateBroker(BrokerBase):
  """
  Mail template broker
  """
  ACTIVATION = 1
  EVENT_PUBLICATION = 2
  EVENT_UPDATE = 3
  PROPOSAL = 4

  def __init__(self, session):
    BrokerBase.__init__(self, session)

  def get_broker_class(self):
    return MailTemplate
