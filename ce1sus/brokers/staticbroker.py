# -*- coding: utf-8 -*-

"""
This module provides container classes of static data

Created: Aug 28, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def invert_dict(dictionary):
  """
  Inverts Key value of a dictionary

  Returns: dictionary
  """
  result = dict()
  for key, value in dictionary.iteritems():
    result[value] = key
  return result


def get_dict_element_by_id(dictionary, identifier):
  """
  Returns an element of a dictionary by identifier if existing.

  Note: identifier has to be an integer

  return object
  """
  identifier = int(identifier)
  if identifier in dictionary.keys():
    value = dictionary[identifier]
  if value:
    return value
  else:
    raise Exception(u'Invalid input "{0}"'.format(identifier))


def get_dict_element_by_value(dictionary, value):
  """
  Returns they key of a dictionary by value if existing.

  return object
  """
  formatted_input = unicode(value).title()
  result = None
  for key, value in dictionary.items():
    if formatted_input == value:
      result = key
      break
  if result is None:
    raise Exception(u'Invalid input "{0}"'.format(value))
  return result


class Status(object):
  """Static class defining the status of an event"""
  __tableDefinitions = {0: 'Confirmed',
                     1: 'Draft',
                     2: 'Deleted',
                     3: 'Expired'}

  def __init__(self, identifier):
    self.identifier = identifier

  @property
  def text(self):
    """Gets the name of the TLP level"""
    return Status.get_by_id(self.identifier)

  @staticmethod
  def get_definitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invert_dict(Status.__tableDefinitions)

  @staticmethod
  def get_by_id(identifier):
    """
    returns the status by the given id

    :returns: String
    """
    return get_dict_element_by_id(Status.__tableDefinitions, identifier)

  @staticmethod
  def get_by_name(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return get_dict_element_by_value(Status.__tableDefinitions, name)


class Analysis(object):
  """Static class defining the status the analysis of an event"""
  __tableDefinitions = {0: 'None',
                     1: 'Opened',
                     2: 'Stalled',
                     3: 'Completed'}

  def __init__(self, identifier):
    self.identifier = identifier

  @property
  def text(self):
    """Gets the name of the TLP level"""
    return Analysis.get_by_id(self.identifier)

  @staticmethod
  def get_definitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invert_dict(Analysis.__tableDefinitions)

  @staticmethod
  def get_by_id(identifier):
    """
    returns the status by the given id

    :returns: String
    """
    return get_dict_element_by_id(Analysis.__tableDefinitions, identifier)

  @staticmethod
  def get_by_name(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return get_dict_element_by_value(Analysis.__tableDefinitions, name)


class Risk(object):
  """Static class defining the risk of an event"""
  __tableDefinitions = {0: 'None',
                     1: 'Low',
                     2: 'Medium',
                     3: 'High'}

  def __init__(self, identifier):
    self.identifier = identifier

  @property
  def text(self):
    """Gets the name of the TLP level"""
    return Risk.get_by_id(self.identifier)

  @staticmethod
  def get_definitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invert_dict(Risk.__tableDefinitions)

  @staticmethod
  def get_by_id(identifier):
    """
    returns the status by the given id

    :returns: String
    """
    return get_dict_element_by_id(Risk.__tableDefinitions, identifier)

  @staticmethod
  def get_by_name(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return get_dict_element_by_value(Risk.__tableDefinitions, name)


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
    return TLPLevel.get_by_id(self.identifier)

  @property
  def color(self):
    """Gets the color of the TLP level"""
    return TLPLevel.get_color_by_id(self.identifier)

  @staticmethod
  def get_by_id(identifier):
    """
    returns the tlp level by the given id

    :returns: String
    """
    return get_dict_element_by_id(TLPLevel.__tlp_levels, identifier)

  @staticmethod
  def get_definitions():
    """
    Returns all definitions where the key is the index and the value the key

    :returns: Dictionary
    """
    return invert_dict(TLPLevel.__tlp_levels)

  @staticmethod
  def get_by_name(name):
    """
    returns the index by the given name

    :returns: Integer
    """
    return get_dict_element_by_value(TLPLevel.__tlp_levels, name)

  @staticmethod
  def get_color_by_id(identifier):
    """
    returns the tlp level color by the given id

    :returns: String
    """
    return get_dict_element_by_id(TLPLevel.__tlp_colors, identifier)
