# -*- coding: utf-8 -*-

"""
module handing the comment pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, requireReferer
from dagr.db.broker import NothingFoundException, ValidationException, \
BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.commentbroker import CommentBroker


class CommentsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.commentBroker = self.brokerFactory(CommentBroker)
    self.eventBroker = self.brokerFactory(EventBroker)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def addComment(self, eventID):
    """
    renders the add a comment page

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event, self.getUser(True))
    template = self.getTemplate('/events/event/comments/commentModal.html')
    return self.cleanHTMLCode(template.render(eventID=eventID,
                           comment=None,
                           errorMsg=None))

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifyComment(self, eventID=None, commentID=None,
                         commentText=None, action=None):
    """
    Modifications of a comment
    """
    template = self.getTemplate('/events/event/comments/commentModal.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event, self.getUser(True))

    comment = self.commentBroker.buildComment(event, self.getUser(), commentID,
                         commentText, action)
    try:
      self.eventBroker.updateEvent(event, False)
      if action == 'insert':
        self.commentBroker.insert(comment, False)
      if action == 'update':
        comment.comment = commentText
        self.commentBroker.update(comment, False)
      if action == 'remove':
        self.commentBroker.removeByID(comment.identifier)
      self.commentBroker.doCommit(True)
      return self.returnAjaxOK()
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      return self.returnAjaxPostError() + self.cleanHTMLCode(
                                                      template.render(
                                                            eventID=eventID,
                             comment=comment))
    except BrokerException as e:
      self.getLogger().fatal(e)
      return 'An unexpected error occurred: {0}'.format(e)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def viewComment(self, eventID, commentID):
    """
     renders the file with the requested comment

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/comments/commentModal.html')
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event, self.getUser(True))
    try:
      comment = self.commentBroker.getByID(commentID)
    except NothingFoundException:
      comment = None
    return self.cleanHTMLCode(template.render(eventID=eventID,
                           comment=comment,
                           errorMsg=None))
