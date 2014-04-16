# -*- coding: utf-8 -*-

"""
module handing the comment pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import ValidationException, BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.commentbroker import CommentBroker


class CommentsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.comment_broker = self.broker_factory(CommentBroker)
    self.event_broker = self.broker_factory(EventBroker)

  def get_by_id(self, comment_id):
    try:
      return self.comment_broker.get_by_id(comment_id)
    except BrokerException as error:
      self._raise_exception(error)

  def insert_comment(self, user, event, comment):
    try:
      try:
        user = self._get_user(user.username)
        self.event_broker.update_event(user, event, commit=False)
        self.comment_broker.insert(comment, commit=False)
        self.comment_broker.do_commit(True)
        return comment, True
      except ValidationException:
        return comment, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_comment(self, user, event, comment):
    """
    Removes an object
    """
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, commit=False)
      self.comment_broker.remove_by_id(comment.identifier, commit=False)
      self.comment_broker.do_commit(True)
      return comment, True
    except BrokerException as error:
      self._raise_exception(error)

  def update_comment(self, user, event, comment):
    try:
      try:
        user = self._get_user(user.username)
        self.event_broker.update_event(user, event, commit=False)
        self.comment_broker.update(comment, commit=False)
        self.comment_broker.do_commit(True)
        return comment, True
      except ValidationException:
        return comment, False
    except BrokerException as error:
      self._raise_exception(error)

  def populate_web_comment(self, identifier, text, event, user, action):
    try:
      user = self._get_user(user.username)
      return self.comment_broker.build_comment(event, user, identifier,
                         text, action)
    except BrokerException as error:
      self._raise_exception(error)
