# -*- coding: utf-8 -*-

"""
This module provides container classes of static data

Created: Aug 28, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

def invertDict(dictionary):
  result = dict()
  for key, value in dictionary.iteritems():
    result[value] = key
  return result


def getDictElementByID(dictionary, identifier):
  identifier = int(identifier)
  if (identifier < 0) and (identifier > len(dictionary)):
    raise Exception('Invalid input "{0}"'.format(identifier))
  return dictionary[identifier]

def getDictElementByValue(dictionary, value):
  formattedInput = unicode(value).title()
  result = None
  for key, value in dictionary.items():
    if formattedInput == value:
      result = key
      break
  if result is None:
    raise Exception('Invalid input "{0}"'.format(value))
  return result

class Status(object):
  """Static class defining the status of an event"""
  __tableDefinitions = {0: 'Confirmed',
                     1: 'Draft',
                     2: 'Deleted',
                     3: 'Expired'}

  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invertDict(Status.__tableDefinitions)

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """
    return getDictElementByID(Status.__tableDefinitions, identifier)


  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return getDictElementByValue(Status.__tableDefinitions, name)



class Analysis(object):
  """Static class defining the status the analysis of an event"""
  __tableDefinitions = {0: 'None',
                     1: 'Opened',
                     2: 'Stalled',
                     3: 'Completed'}

  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invertDict(Analysis.__tableDefinitions)


  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """
    return getDictElementByID(Analysis.__tableDefinitions, identifier)

  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return getDictElementByValue(Analysis.__tableDefinitions, name)


class Risk(object):
  """Static class defining the risk of an event"""
  __tableDefinitions = {0: 'None',
                     1: 'Low',
                     2: 'Medium',
                     3: 'High'}

  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invertDict(Risk.__tableDefinitions)

  @staticmethod
  def getByID(identifier):
    """
    returns the status by the given id

    :returns: String
    """
    return getDictElementByID(Risk.__tableDefinitions, identifier)

  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return getDictElementByValue(Risk.__tableDefinitions, name)


class TLPLevel(object):
  """Static class defining the TLP levels of an event"""
  __tlp_levels = {0: 'Red',
                1: 'Amber',
                2: 'Green',
                3: 'White'}
  __tlp_colors = {0: '#FF0000',
                1: '#FFBF00',
                2: '#66B032',
                3: '#FFFFFF'}

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
    return getDictElementByID(TLPLevel.__tlp_levels, identifier)

  @staticmethod
  def getDefinitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invertDict(TLPLevel.__tlp_levels)

  @staticmethod
  def getByName(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return getDictElementByValue(TLPLevel.__tlp_levels, name)

  @staticmethod
  def getColorByID(identifier):
    """
    returns the tlp level color by the given id

    :returns: String
    """
    return getDictElementByID(TLPLevel.__tlp_colors, identifier)
