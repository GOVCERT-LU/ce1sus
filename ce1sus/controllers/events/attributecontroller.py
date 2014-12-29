# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.attributebroker import AttributeBroker
from ce1sus.db.common.broker import ValidationException, IntegrityException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    BaseController.__init__(self, config)
    self.attribute_broker = self.broker_factory(AttributeBroker)

  def insert_attribute(self, attribute, user, commit=True):
    """
    inserts an event

    If it is invalid the event is returned

    :param event:
    :type event: Event

    :returns: Event, Boolean
    """
    self.logger.debug('User {0} inserts a new event'.format(user.username))
    try:

      user = self.user_broker.get_by_id(user.identifier)
      self.set_extended_logging(attribute, user, user.group, True)
      self.attribute_broker.insert(attribute, False)
      # generate relations if needed!

      """
      attributes = get_all_attributes_from_event(event)
      if (mkrelations == 'True' or mkrelations is True) and attributes:
        self.relation_broker.generate_bulk_attributes_relations(event, attributes, False)
      """
      self.attribute_broker.do_commit(commit)
      return attribute, True
    except ValidationException:
      return attribute, False
    except IntegrityException as error:
      self.logger.debug(error)
      self.logger.info(u'User {0} tried to insert an event with uuid "{1}" but the uuid already exists'.format(user.username, attribute.identifier))
      raise ControllerException(u'An event with uuid "{0}" already exists'.format(attribute.identifier))
    except BrokerException as error:
      raise ControllerException(error)
