__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

"""General exceptions"""

class InstantiationException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class NothingFoundException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class TooManyResultsFoundException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)
