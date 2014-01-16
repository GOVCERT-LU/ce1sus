# -*- coding: utf-8 -*-

"""
module in charge of string foo, since cherrypy sends more parameters

Created Aug, 2013
"""
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import dagr.helpers.strings as strings


# pylint: disable=W0613
def plaintext2html(context, text, tabstop=4):
  """
  Converts plain text string to html
  """
  stringText = strings.plaintext2html(text, tabstop)

  return stringText
