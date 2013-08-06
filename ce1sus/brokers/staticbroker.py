"""This module provides container classes of static data"""

class Type(object):
  """Static class defining the types of an object"""
  __definitions = {0 : 'Virus',
                   1 : 'Trojan',
                   2 : 'Expoit',
                   3 : 'Dropper',
                   4 : 'KeyLogger',
                   5 : 'BackDoor',
                   6 : 'Worm'}

  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    result = dict()
    for key, value in Type.__definitions.iteritems():
      result[value] = key
    return result

class Status(object):
  """Static class defining the status of an event"""
  __definitions = {0 : 'Draft',
                     1 : 'Confirmed',
                     2 : 'Expired',
                     3 : 'Deleted'}


  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    result = dict()
    for key, value in Status.__definitions.iteritems():
      result[value] = key
    return result

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """

    identifier = int(identifier)

    if identifier < 0 and identifier > len(Status.__definitions):
      raise Exception('Invalid input "{0}"'.format(identifier))
    return Status.__definitions[identifier]



  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    formattedInput = str(name).title()
    result = None
    for key, value in Status.__definitions.items():
      if formattedInput == value:
        result = key
        break
    if result is None:
      raise Exception('Invalid input "{0}"'.format(name))


class TLPLevel(object):
  """Static class defining the TLP levels of an event"""
  __tlp_levels = {0 : 'Red',
                1 : 'Amber',
                2 : 'Green',
                3 : 'White'}

  __tlp_colors = {0 : '#FF0000',
                1 : '#FFBF00',
                2 : '#66B032',
                3 : '#FFFFFF'}

  def __init__(self, identifier):
    self.identifier = identifier

  @property
  def text(self):
    """Gets the name of the TLP level"""
    return TLPLevel.getByID(self.identifier)

  @property
  def color(self):
    """Gets the color of the TLP level"""
    return TLPLevel.getColorByID(self.identifier)

  @staticmethod
  def getByID(identifier):
    """
    returns the tlp level by the given id

    :returns: String
    """

    identifier = int(identifier)

    if identifier < 0 and identifier > 3:
      raise Exception('Invalid input "{0}"'.format(identifier))

    return TLPLevel.__tlp_levels[identifier]



  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    result = dict()
    for key, value in TLPLevel.__tlp_levels.iteritems():
      result[value] = key
    return result


  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """

    formatedName = str(name).title()


    result = None
    for key, value in TLPLevel.__tlp_levels.items():
      if formatedName == value:
        result = key
        break
    if result is None:
      raise Exception('Invalid input "{0}"'.format(name))

  @staticmethod
  def getColorByID(identifier):
    """
    returns the tlp level color by the given id

    :returns: String
    """
    identifier = int(identifier)

    if identifier < 0 and identifier > 3:
      raise Exception('Invalid input "{0}"'.format(identifier))
    return TLPLevel.__tlp_colors[identifier]

