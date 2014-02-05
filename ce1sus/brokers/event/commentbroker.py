# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 9, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException
import sqlalchemy.orm.exc
from dagr.helpers.datumzait import DatumZait
from ce1sus.brokers.event.eventclasses import Comment
from dagr.helpers.strings import cleanPostValue


class CommentBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getAllByEventID(self, eventID):
    """
    Returns all the comments belonging to one event

    :param eventID: identifier of the event
    :type eventID: Integer

    :returns: List of Comments
    """
    try:

      result = self.session.query(Comment).filter(
                        Comment.event_id == eventID).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with event ID :{0}'.format(
                                                                  eventID))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return result

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Comment

  # pylint: disable=R0913
  def build_comment(self, event, user, comment_id=None,
                         comment_text=None, action=None):
    """
    Modifications of a comment
    """
    comment = Comment()
    if not action == 'insert':
      comment = self.get_by_id(comment_id)
    comment.modified = DatumZait.utcnow()
    comment.modifier = user
    comment.modifier_id = comment.modifier.identifier
    comment.comment = cleanPostValue(comment_text)
    if action == 'insert':
      comment.creator = user
      comment.creator_id = comment.creator.identifier
      comment.event = event
      comment.event_id = event.identifier
      comment.created = DatumZait.utcnow()
    return comment
