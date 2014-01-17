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
from dagr.helpers.config import Configuration
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
  def __init__(self, configFile):
    config = Configuration(configFile, 'ErrorHandler')
    ErrorHandler.__debug = config.get('debug')
    cherrypy.config.update({'error_page.400': ErrorHandler.error_page_400})
    cherrypy.config.update({'error_page.401': ErrorHandler.error_page_401})
    cherrypy.config.update({'error_page.403': ErrorHandler.error_page_403})
    cherrypy.config.update({'error_page.404': ErrorHandler.error_page_404})
    cherrypy.config.update({'error_page.500': ErrorHandler.error_page_500})
    cherrypy.config.update({'request.error_response':
                            ErrorHandler.handle_error})
    ErrorHandler.__sendMail = config.get('useMailer')
    ErrorHandler.__receiver = config.get('receiver')
    ErrorHandler.__subject = config.get('subject')

  @staticmethod
  def blueScreen(title='500', error='DEFAULT', text='DEFAULT MESSAGE'):
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
    return (MakoHandler.getInstance().
                              renderTemplate("/dagr/errors/blueScreen.html",
                                                    title=title,
                                                    error=error,
                                                    text=text))

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
    return (MakoHandler.getInstance().
                                renderTemplate("/dagr/errors/errorC64.html",
                                                    title=title,
                                                    error=error,
                                                    version=version,
                                                    text=text))

  @staticmethod
  def show(title='500', error='DEFAULT', text='DEFAULT MESSAGE', version='2', sendMail=True, message='Default Error'):
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

    if (ErrorHandler.__sendMail and ErrorHandler.__receiver and sendMail):
      # create mail
      mailMessage = Mail()
      mailMessage.body = 'Error: {0}\n\nOccured On:{1}\n\nStackTrace:\n{2}'.format(message, datetime.now(), text)
      mailMessage.subject = ErrorHandler.__subject
      if not mailMessage.subject:
        mailMessage.subject = 'An error Occured'
      mailMessage.reciever = ErrorHandler.__receiver
      try:
        mailer = Mailer.getInstance()
        mailer.sendMail(mailMessage)
      except MailerException as e:
         Log.getLogger(__name__).critical('Could not send mail Mailer not instantiated:{0}', e)

    # TODO: random error screen
    return ErrorHandler.commodore(title, stringHelper.plaintext2html(error), stringHelper.plaintext2html(restext), version)

  @staticmethod
  def handle_error():
    """
    handle_error
    """
    # this error handling works different than the others
    cherrypy.response.status = 500
    # Default
    Log.getLogger(__name__).critical('Default error: '
                                        + traceback.format_exc())
    cherrypy.response.body = ErrorHandler.show(title='500',
                                              error='2^255*8-2^1024\n'
                                              + 'FORMULA TOO COMPLEX',
                                              text=
                                                      traceback.format_exc(),
                                                      message='Unkown Error')

  # pylint: disable=W0621
  @staticmethod
  def error_page_400(status, message, traceback, version):
    """
    handle_error
    """
    # Bad Request
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='400', error=message + '\n?SYNTAX ERROR.'
                             + '\n\n', text=traceback,
                             version=version,
                             sendMail=True,
                                                      message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_401(status, message, traceback, version):
    """
    handle_error
    """
    # Unauthorized
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='401', error=message + '\n?SYNTAX ERROR.'
                             + '\n\n', text=
                                                                    traceback,
                             version=version,
                             sendMail=True,
                                                      message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_403(status, message, traceback, version):
    """
    handle_error
    """
    # Forbiden
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='403', error=message + '\n?SYNTAX ERROR.'
                             + '\n\n', text=
                                                                    traceback,
                             version=version,
                                                      message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_404(status, message, traceback, version):
    """
    handle_error
    """
    # Not Found
    Log.getLogger(__name__).error(message)

    matchObj = re.match(r".*'(.*)'.*", message, re.M | re.I)
    fileName = matchObj.group(1)
    return  ErrorHandler.show(title='404', error='LOAD "' + fileName + '", 8'
                              + '\nLOADING\n\nFILE NOT FOUND',
                              text=traceback,
                             version=version,
                             sendMail=False,
                                                      message=message)

  # pylint: disable=W0621
  @staticmethod
  def error_page_500(status, message, traceback, version):
    """
    handle_error
    """
    # Internal Error
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='500', error=message + '\nFORMULA TOO '
                            + 'COMPLEX\n', text=
                                                                   traceback,
                             version=version,
                             sendMail=True,
                                                      message=message)
