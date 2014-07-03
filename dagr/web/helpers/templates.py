# -*- coding: utf-8 -*-

"""
module providing support for template handling

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from tempfile import gettempdir
from mako.lookup import TemplateLookup


class MakoHandler(object):
  """Helper class for MAKO templates"""

  def __init__(self, config):
    """
    Creator for the Mako handler

    :param config: The configuration for this module
    :type config: Configuration

    :returns: MakoHandler
    """
    config_section = config.get_section('Mako')
    tmp_folder = config_section.get('tmpfolder')
    self.__mylookup = TemplateLookup(directories=[config_section.get('templateroot'),
                                                  config_section.get('projectroot')],
                                     module_directory=tmp_folder + '/mako_modules',
                                     collection_size=config_section.get('collectionsize'),
                                     output_encoding=config_section.get('outputencoding'),
                                     encoding_errors='replace')

  def get_template(self, templatename):
    """
    Returns the template by the given name

    :param templatename: The name of the template
    :type templatename: String

    :returns: Template
    """
    return self.__mylookup.get_template(templatename)

  def render_template(self, templatename, **args):
    """
    Gets the template and renders it directly with the given arguments

    :returns: generated HTML
    """
    mytemplate = self.get_template(templatename)
    return mytemplate.render_unicode(**args)
