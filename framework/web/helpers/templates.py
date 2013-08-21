"""module providing support for template handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.helpers.config import Configuration
from tempfile import gettempdir
from mako.lookup import TemplateLookup

class MakoHandler(object):
  """Helper class for MAKO templates"""
  def __init__(self, configFile):

    config = Configuration(configFile, 'Mako')

    templateRoot = config.get('templateroot')
    collectionSize = config.get('collectionsize')
    outputEncoding = config.get('outputencoding')
    self.__mylookup = TemplateLookup(directories=[templateRoot],
                              module_directory=gettempdir() + '/mako_modules',
                              collection_size=collectionSize,
                              output_encoding=outputEncoding,
                              encoding_errors='replace')

    MakoHandler.instance = self


  def getTemplate(self, templatename):
    """
    Returns the template by the given name

    :param templatename: The name of the template
    :type templatename: String

    :returns: Template
    """
    return self.__mylookup.get_template(templatename)

  def renderTemplate(self, templatename, **kwargs):
    """
    Gets the template and renders it directly with the given arguments

    :returns: generated HTML
    """
    mytemplate = self.__mylookup.get_template(templatename)
    return mytemplate.render_unicode(**kwargs)

  @staticmethod
  def getInstance():
    """
    Returns the instance of the template handler.

    :returns: MakoHandler
    """
    if MakoHandler.instance == None:
      raise IndentationError('No MakoHandler present')
    return MakoHandler.instance
