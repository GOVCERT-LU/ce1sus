"""module in charge of all pagination stuff"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class PaginatorOptions(object):
  # MODE = Enum(MODAL=0, LINK=1, DIALOG=2, CONTENT=3, NEWTAB=4,TAB=5)
  # OPTION = Enum(VIEW=0, EDIT=1, REMOVE=2)

  ICON_MAPPER = {'VIEW':'icon-eye-open',
                 'EDIT':'icon-pencil',
                 'REMOVE':'icon-remove'}

  TITLE_MAPPER = {'VIEW':'View',
                  'EDIT':'Edit',
                  'REMOVE':'Remove'}
  MSG_MAPPER = {'VIEW':'',
                'EDIT':'',
                'REMOVE':'Are you sure you want to delete?'}

  class Option(object):
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
      return PaginatorOptions.ICON_MAPPER[self.option]

    @property
    def title(self):
      return PaginatorOptions.ICON_MAPPER[self.option]

    @property
    def message(self):
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

