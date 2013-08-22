"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import copy
from framework.web.controllers.base import BaseController
import cherrypy
from ce1sus.web.helpers.protection import require
from ce1sus.brokers.eventbroker import EventBroker, Comment, CommentBroker
from ce1sus.web.helpers.protection import privileged
from datetime import datetime
from framework.db.broker import NothingFoundException, ValidationException, \
BrokerException

class CommentsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.commentBroker = self.brokerFactory(CommentBroker)
    self.eventBroker = self.brokerFactory(EventBroker)

  @require(privileged())
  @cherrypy.expose
  def addComment(self, eventID):
    """
    renders the events page

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/comments/commentModal.html')
    return template.render(eventID=eventID,
                           comment=None,
                           errorMsg=None)

  @cherrypy.expose
  @require()
  def modifyComment(self, eventID=None, commentID=None,
                         commentText=None, action=None):
    """
    Modifications of a comment
    """
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)

    comment = Comment()
    errorMsg = ''
    if not action == 'insert':
      comment_orig = self.commentBroker.getByID(commentID)
      # dont want to change the original in case the user cancel!
      comment = copy.copy(comment_orig)

    if action == 'insert':
      comment.comment = commentText
      comment.creator = self.getUser()
      comment.user_id = comment.creator.identifier
      comment.event = event
      comment.event_id = event.identifier
      comment.created = datetime.now()

      try:
        self.commentBroker.insert(comment)
      except ValidationException:
        self.getLogger().debug('Event is invalid')
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)

    if action == 'update':
      comment.comment = commentText

      try:
        self.commentBroker.update(comment)
      except ValidationException:
        self.getLogger().debug('Event is invalid')
        errorMsg = 'Object Invalid'
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)

    if action == 'remove':
      try:
        self.commentBroker.removeByID(comment.identifier)
      except ValidationException:
        self.getLogger().debug('Event is invalid')
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)

    if errorMsg:
      template = self.getTemplate('/events/event/comments/commentModal.html')
      return template.render(eventID=eventID,
                             comment=comment,
                             errorMsg=errorMsg)
    else:
      return self.returnAjaxOK()

  @cherrypy.expose
  @require()
  def viewComment(self, eventID=None, commentID=None):
    """
     renders the file with the requested comment

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/comments/commentModal.html')

    try:
      comment = self.commentBroker.getByID(commentID)
    except NothingFoundException:
      comment = None
    return template.render(eventID=eventID,
                           comment=comment,
                           errorMsg=None)
