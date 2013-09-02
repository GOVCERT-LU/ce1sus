"""This module provides container classes of static data"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Type(object):
  """Static class defining the types of an object"""
  __tableDefinitions = {0 : 'Virus',
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
    for key, value in Type.__tableDefinitions.iteritems():
      result[value] = key
    return result

  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """

    formatedName = unicode(name).title()


    result = None
    for key, value in Type.__tableDefinitions.items():
      if formatedName == value:
        result = key
        break
    if result is None:
      raise Exception('Invalid input "{0}"'.format(name))

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """

    identifier = int(identifier)

    if identifier < 0 and identifier > len(Type.__tableDefinitions):
      raise Exception('Invalid input "{0}"'.format(identifier))
    return Type.__tableDefinitions[identifier]

class Status(object):
  """Static class defining the status of an event"""
  __tableDefinitions = {0 : 'Draft',
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
    for key, value in Status.__tableDefinitions.iteritems():
      result[value] = key
    return result

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """

    identifier = int(identifier)

    if identifier < 0 and identifier > len(Status.__tableDefinitions):
      raise Exception('Invalid input "{0}"'.format(identifier))
    return Status.__tableDefinitions[identifier]

  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """

    formatedName = unicode(name).title()


    result = None
    for key, value in Status.__tableDefinitions.items():
      if formatedName == value:
        result = key
        break
    if result is None:
      raise Exception('Invalid input "{0}"'.format(name))

class Analysis(object):
  """Static class defining the status the analysis of an event"""
  __tableDefinitions = {0 : 'None',
                     1 : 'Opened',
                     2 : 'Stalled',
                     3 : 'Completed'}


  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    result = dict()
    for key, value in Analysis.__tableDefinitions.iteritems():
      result[value] = key
    return result

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """

    identifier = int(identifier)

    if identifier < 0 and identifier > len(Analysis.__tableDefinitions):
      raise Exception('Invalid input "{0}"'.format(identifier))
    return Analysis.__tableDefinitions[identifier]



  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    formattedInput = unicode(name).title()
    result = None
    for key, value in Analysis.__tableDefinitions.items():
      if formattedInput == value:
        result = key
        break
    if result is None:
      raise Exception('Invalid input "{0}"'.format(name))


class Risk(object):
  """Static class defining the risk of an event"""
  __tableDefinitions = {0 : 'None',
                     1 : 'Low',
                     2 : 'Medium',
                     3 : 'High'}


  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    result = dict()
    for key, value in Risk.__tableDefinitions.iteritems():
      result[value] = key
    return result

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """

    identifier = int(identifier)

    if identifier < 0 and identifier > len(Risk.__tableDefinitions):
      raise Exception('Invalid input "{0}"'.format(identifier))
    return Risk.__tableDefinitions[identifier]

  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """

    formatedName = unicode(name).title()


    result = None
    for key, value in Risk.__tableDefinitions.items():
      if formatedName == value:
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

    formatedName = unicode(name).title()


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

