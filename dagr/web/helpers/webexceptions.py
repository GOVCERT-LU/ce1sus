# -*- coding: utf-8 -*-

"""
module providing the error handling

Created: Jul, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
import traceback
import dagr.helpers.strings as stringHelper
from dagr.helpers.debug import Log
from dagr.web.helpers.templates import MakoHandler
import re
from dagr.helpers.mailer import Mailer, Mail, MailerException
from datetime import datetime


class ErrorHandler(object):
  """
    Generic ErrorHandler for cherrypy projects

    Note: Expects templates
  """
  def __init__(self, config):
    config_section = config.get_section('ErrorHandler')
    ErrorHandler.__debug = config_section.get('debug')
    cherrypy.config.update({'error_page.400': ErrorHandler.error_page_400})
    cherrypy.config.update({'error_page.401': ErrorHandler.error_page_401})
    cherrypy.config.update({'error_page.403': ErrorHandler.error_page_403})
    cherrypy.config.update({'error_page.404': ErrorHandler.error_page_404})
    cherrypy.config.update({'error_page.500': ErrorHandler.error_page_500})
    cherrypy.config.update({'request.error_response':
                            ErrorHandler.handle_error})
    ErrorHandler.sendMail = config_section.get('usemailer')
    ErrorHandler.receiver = config_section.get('receiver')
    ErrorHandler.subject = config_section.get('subject')
    ErrorHandler.mako = MakoHandler(config)
    ErrorHandler.logger = Log(config)
    ErrorHandler.mailer = Mailer(config)

  @staticmethod
  def _get_logger():
    """Returns the class logger"""
    return ErrorHandler.logger.get_logger('ErrorHandler')

  @staticmethod
  def blue_screen(title='500', error='DEFAULT', text='DEFAULT MESSAGE'):
    """
    Renders the blue screen error page

    :param title: The title of the page
    :type title: String
    :param error: Error which occured
    :type error: String
    :param text: Additional information about the error
    :tyoe
    :returns: generated HTML
    """
    return ErrorHandler.mako.render_template("/dagr/errors/blue_screen.html",
                                                    title=title,
                                                    error=error,
                                                    text=text)

  @staticmethod
  def commodore(title='500',
                error='DEFAULT',
                text='DEFAULT MESSAGE',
                version='2'):
    """
    Renders the commodore error page

    :param title: The title of the page
    :type title: String
    :param error: Error which occured
    :type error: String
    :param text: Additional information about the error
    :tyoe
    :returns: generated HTML
    """
    return ErrorHandler.mako.render_template("/dagr/errors/errorC64.html",
                                                    title=title,
                                                    error=error,
                                                    version=version,
                                                    text=text)

  @staticmethod
  def show(title='500', error='DEFAULT', text='DEFAULT MESSAGE', version='2', send_mail=True, message='Default Error'):
    """
    Renders the error page

    :param title: The title of the page
    :type title: String
    :param error: Error which occured
    :type error: String
    :param text: Additional information about the error
    :tyoe
    :returns: generated HTML
    """

    if ErrorHandler.__debug:
      restext = text
    else:
      restext = None
    config_settings = ErrorHandler.sendMail and ErrorHandler.receiver
    if  config_settings and send_mail:
      # create mail
      mail_message = Mail()
      mail_message.body = 'Error: {0}\n\nOccured On:{1}\n\nStackTrace:\n{2}'.format(message, datetime.now(), text)
      mail_message.subject = ErrorHandler.subject
      if not mail_message.subject:
        mail_message.subject = 'An error Occured'
      mail_message.reciever = ErrorHandler.receiver
      try:
        ErrorHandler.mailer.send_mail(mail_message)
      except MailerException as err:
        ErrorHandler._get_logger().critical('Could not send mail Mailer not instantiated:{0}', err)

    # TODO: random error screen
    return ErrorHandler.commodore(title,
                                  stringHelper.plaintext2html(error),
                                  stringHelper.plaintext2html(restext),
                                  version)

  @staticmethod
  def handle_error():
    """
    handle_error
    """
    # this error handling works different than the others
    cherrypy.response.status = 500
    # Default
    ErrorHandler._get_logger().critical('Default error: '
                                        + traceback.format_exc())
    cherrypy.response.body = ErrorHandler.show(title='500',
                                              error='2^255*8-2^1024\n'
                                              + 'FORMULA TOO COMPLEX',
                                              text=traceback.format_exc(),
                                              message='Unkown Error')

  # pylint: disable=W0621
  @staticmethod
  def error_page_400(status, message, traceback, version):
    """
    handle_error
    """
    if status:
      pass
    # Bad Request
    ErrorHandler._get_logger().error(message)
    return ErrorHandler.show(title='400', error=message + '\n?SYNTAX ERROR.'
                             + '\n\n', text=traceback,
                             version=version,
                             send_mail=True,
                                                      message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_401(status, message, traceback, version):
    """
    handle_error
    """
    if status:
      pass
    # Unauthorized
    ErrorHandler._get_logger().error(message)
    return ErrorHandler.show(title='401', error=message + '\n?SYNTAX ERROR.'
                             + '\n\n', text=
                                                                    traceback,
                             version=version,
                             send_mail=True,
                                                      message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_403(status, message, traceback, version):
    """
    handle_error
    """
    if status:
      pass
    # Forbiden
    ErrorHandler._get_logger().error(message)
    return ErrorHandler.show(title='403',
                             error=message + '\n?SYNTAX ERROR.\n\n',
                             text=traceback,
                             version=version,
                             message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_404(status, message, traceback, version):
    """
    handle_error
    """
    if status:
      pass
    # Not Found
    ErrorHandler._get_logger().error(message)

    match_obj = re.match(r".*'(.*)'.*", message, re.M | re.I)
    file_name = match_obj.group(1)
    return  ErrorHandler.show(title='404', error='LOAD "' + file_name + '", 8'
                              + '\nLOADING\n\nFILE NOT FOUND',
                              text=traceback,
                             version=version,
                             send_mail=False,
                             message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_500(status, message, traceback, version):
    """
    handle_error
    """
    if status:
      pass
    # Internal Error
    ErrorHandler._get_logger().error(message)
    return ErrorHandler.show(title='500', error=message + '\nFORMULA TOO COMPLEX\n',
                             text=traceback,
                             version=version,
                             send_mail=True,
                             message=message)
