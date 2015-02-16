# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 30, 2014
"""
from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.mail_controller = MailController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT'])
  @require(privileged())
  def mail(self, **args):
    try:
      method = args.get('method')
      json = args.get('json')
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      if method == 'GET':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single mail
          uuid = path.pop(0)
          mail = self.mail_controller.get_by_uuid(uuid)
          return mail.to_dict(details, inflated)
        else:
          # return all
          mails = self.mail_controller.get_all()
          result = list()
          for mail in mails:
            result.append(mail.to_dict(details, inflated))
          return result
      elif method == 'PUT':
        if len(path) > 0:
          uuid = path.pop(0)
          mail = self.mail_controller.get_by_uuid(uuid)
          mail.populate(json)
          self.mail_controller.update_mail(mail, self.get_user())
          return mail.to_dict(details, inflated)
        else:
          raise RestHandlerException(u'Cannot update user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
