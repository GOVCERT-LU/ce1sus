# -*- coding: utf-8 -*-

"""
module in charge of all pagination stuff

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Link(object):
  """
  Container class for links
  """
  def __init__(self, urlBase, identifier):
    self.urlBase = urlBase
    self.identifier = identifier

  @property
  def url(self):
    """
    Returns an formatted url

    :returns: String
    """
    return '{0}{1}'.format(self.urlBase, self.identifier)

class PaginatorOptions(object):
  """
  Option class for the paginator
  """
  # MODE = Enum(MODAL=0, LINK=1, DIALOG=2, CONTENT=3, NEWTAB=4,TAB=5)
  # OPTION = Enum(VIEW=0, EDIT=1, REMOVE=2)

  ICON_MAPPER = {'VIEW':'glyphicon glyphicon-eye-open',
                 'EDIT':'glyphicon glyphicon-edit',
                 'REMOVE':'glyphicon glyphicon-remove'}

  TITLE_MAPPER = {'VIEW':'View',
                  'EDIT':'Edit',
                  'REMOVE':'Remove'}
  MSG_MAPPER = {'VIEW':'',
                'EDIT':'',
                'REMOVE':'Are you sure you want to delete?'}

  class Option(object):
    """
    Option container class
    """
    def __init__(self,
                 option,
                 mode,
                 url,
                 message='',
                 contentid='',
                 refresh=False,
                 tabid='',
                 modalTitle='',
                 postUrl=''):
      self.option = option
      self.mode = mode
      self.url = url
      self.text = message
      self.contentid = contentid
      self.refresh = refresh
      self.tabid = tabid
      self.modalTitle = modalTitle
      self.postUrl = postUrl
    @property
    def icon(self):
      """
      Returns the name of the icon used

      :returns: String
      """
      return PaginatorOptions.ICON_MAPPER[self.option]

    @property
    def title(self):
      """
      Returns the title for the option

      :returns: String
      """
      return PaginatorOptions.TITLE_MAPPER[self.option]

    @property
    def message(self):
      """
      Returns the message

      :returns: String
      """
      if not self.text:
        # return default
        return PaginatorOptions.MSG_MAPPER[self.option]
      else:
        return self.text

  def __init__(self, reloadUrl='', contentid=''):
    self.options = list()
    self.reloadUrl = reloadUrl
    self.contentid = contentid

  def addOption(self,
                mode,
                option,
                url,
                message='',
                contentid='',
                refresh=False,
                tabid='',
                modalTitle='',
                postUrl=''):
    """
    Adds an option

    :param mode: The mode in which the option operates
                 i.e.:  # MODAL, LINK, DIALOG, CONTENT, NEWTAB,TAB
    :type mode: String
    :param option: The option wich it is
                   i.e.:VIEW, EDIT, REMOVE
    :type option: String
    :param url: The url of the content to be displayed
                (works not with the mode Dialog)
    :type url: String
    :param message: The message to be displayed
                    (works only with the mode Dialog)
    :type message: String
    :param contentid: The conentid to display the url
    :type contentid: String
    :param refresh: Refresh the contentid?
    :type refresh: Boolean
    :param tabid: The id of the tab
    :type tabid: String
    :param modalTitle: The title of the modal window
    :type modalTitle: String
    :param postUrl: The url to post to
    :type postUrl: String
    """
    option = PaginatorOptions.Option(option,
                                     mode,
                                     url,
                                     message,
                                     contentid,
                                     refresh,
                                     tabid,
                                     modalTitle,
                                     postUrl)
    self.options.append(option)

  @property
  def isSet(self):
    """
    Checks if there are options set

    :returns: Boolean
    """
    return len(self.options) > 0



class Paginator(object):
  """Definition class for the pagintor on the HTML page"""

  def __init__(self,
               items,
               labelsAndProperty,
               paginatorOptions=PaginatorOptions(),
               itemsPerPage=10):
    self.lables = labelsAndProperty
    self.list = items
    self.options = paginatorOptions
    self.itemsPerPage = itemsPerPage

