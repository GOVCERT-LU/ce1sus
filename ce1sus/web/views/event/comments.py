# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 1, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.views.base import Ce1susBaseView
from ce1sus.controllers.event.comments import CommentsController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class CommentsView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.comments_controller = CommentsController(config)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def add_comment(self, event_id):
    """
    renders the add a comment page

    :returns: generated HTML
    """
    try:
      event = self.comments_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      return self._render_template('/events/event/comments/commentModal.html',
                                   event_id=event_id,
                                   comment=None)
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def view_comment(self, event_id, comment_id):
    """
     renders the file with the requested comment

    :returns: generated HTML
    """
    try:
      event = self.comments_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      comment = self.comments_controller.get_by_id(comment_id)
      return self._render_template('/events/event/comments/commentModal.html',
                                     event_id=event_id,
                                     comment=comment)
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def modify_comment(self, event_id=None, comment_id=None,
                         comment_text=None, action=None):
    try:
      event = self.comments_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      user = self._get_user()
      comment = self.comments_controller.populate_web_comment(comment_id, comment_text, event, user, action)
      if action == 'insert':
        comment, valid = self.comments_controller.insert_comment(user, event, comment)
        if not valid:
          self._get_logger().info('Comment is invalid')
          return self._return_ajax_post_error(self._render_template('/events/event/comments/commentModal.html',
                                                          event_id=event_id,
                                                          comment=comment))
      if action == 'update':
        comment, valid = self.comments_controller.update_comment(user, event, comment)
        if not valid:
          self._get_logger().info('Comment is invalid')
          return self._return_ajax_post_error(self._render_template('/events/event/comments/commentModal.html',
                                                          event_id=event_id,
                                                          comment=comment))
      if action == 'remove':
        self.comments_controller.remove_comment(user, event, comment)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)
