# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 23, 2015
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.definitions.typebrokers import IndicatorTypeBroker
from ce1sus.db.classes.indicator import IndicatorType
from ce1sus.db.common.broker import BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IndicatorController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.indicator_type_broker = self.broker_factory(IndicatorTypeBroker)

  def get_all(self):
    try:
      return self.indicator_type_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_types(self):
    result = list()
    for key in IndicatorType.get_dictionary().iterkeys():
        it = IndicatorType()
        it.type = key
        result.append(it)
    return result
