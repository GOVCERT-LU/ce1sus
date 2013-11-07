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
import dagr.helpers.string as stringHelper
from dagr.helpers.debug import Log
from dagr.web.helpers.templates import MakoHandler
import re


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
  def show(title='500', error='DEFAULT', text='DEFAULT MESSAGE', version='2'):
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

    # TODO: random error
    if ErrorHandler.__debug:
      restext = text
    else:
      restext = None
    return ErrorHandler.commodore(title, error, restext, version)

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
                                              error='2^255*8-2^1024<br/>'
                                              + 'FORMULA TOO COMPLEX',
                                              text=stringHelper.plaintext2html(
                                                      traceback.format_exc()))

  @staticmethod
  def error_page_400(status, message, traceback, version):
    """
    handle_error
    """
    # Bad Request
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='400', error=message + '<br/>?SYNTAX ERROR.'
                             + '<br/><br/>', text=stringHelper.plaintext2html(
                                                                    traceback))

  @staticmethod
  def error_page_401(status, message, traceback, version):
    """
    handle_error
    """
    # Unauthorized
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='401', error=message + '<br/>?SYNTAX ERROR.'
                             + '<br/><br/>', text=stringHelper.plaintext2html(
                                                                    traceback))

  @staticmethod
  def error_page_403(status, message, traceback, version):
    """
    handle_error
    """
    # Forbiden
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='403', error=message + '<br/>?SYNTAX ERROR.'
                             + '<br/><br/>', text=stringHelper.plaintext2html(
                                                                    traceback),
                             version=version)

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
                              + '<br/>LOADING<br/><br/>FILE NOT FOUND',
                              text=stringHelper.plaintext2html(traceback))

  @staticmethod
  def error_page_500(status, message, traceback, version):
    """
    handle_error
    """
    # Internal Error
    Log.getLogger(__name__).error(message)
    return ErrorHandler.show(title='500', error=message + '<br/>FORMULA TOO '
                            + 'COMPLEX<br/>', text=stringHelper.plaintext2html(
                                                                   traceback))
