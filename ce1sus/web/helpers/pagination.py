"""module in charge of all pagination stuff"""

class Paginator(object):
  """Definition class for the pagintor on the HTML page"""

  def __init__(self, items,
               labelsAndProperty,
               baseUrl,
               showOptions=False,
               itemsPerPage=10):

    self.lables = labelsAndProperty
    self.list = items
    self.baseUrl = baseUrl

    self.showOptions = showOptions
    if (self.showOptions):
      self.__view = True
      self.__edit = True
      self.__delete = True
    else:
      self.__view = False
      self.__edit = False
      self.__delete = False
    self.itemsPerPage = itemsPerPage


  @property
  def showView(self):
    """
    Is true if the view option should be shown

    :returns: Boolean
    """
    return self.__view
  @showView.setter
  def showView(self, value):
    """
    Sets the value for the showView property

    :param value: the value to be set
    :type value: Boolean
    """
    self.showOptions = value
    self.__view = value

  @property
  def showEdit(self):
    """
    Is true if the edit option should be shown

    :returns: Boolean
    """
    return self.__edit
  @showEdit.setter
  def showEdit(self, value):
    """
    Sets the value for the showEdit property

    :param value: the value to be set
    :type value: Boolean
    """
    self.showOptions = value
    self.__edit = value

  @property
  def showDelete(self):
    """
    Is true if the delete option should be shown

    :returns: Boolean
    """
    return self.__delete
  @showDelete.setter
  def showDelete(self, value):
    """
    Sets the value for the showDelete property

    :param value: the value to be set
    :type value: Boolean
    """
    self.showOptions = value
    self.__delete = value

