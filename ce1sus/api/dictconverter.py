# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 6, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.api.restclasses import RestClass
from dagr.helpers.converters import convert_string_to_value
from dagr.helpers.debug import Log
from datetime import datetime
from types import DictionaryType, ListType
from dagr.helpers.objects import get_class


class DictConversionException(Exception):
  """Base exception for this class"""
  pass


class DictConverter(object):
  """Class converts a dict to an object an visversa"""

  def __init__(self, config):
    self.__config = config
    self.logger = Log(config)

  def _get_logger(self):
    """Returns the class logger"""
    return self.logger.get_logger(self.__class__.__name__)

  def __map_dict_to_object(self, dictionary):
    """ maps dictionary to rest objects"""
    self._get_logger().debug(u'Start mapping dictionary to object')
    start_time = datetime.now()
    if dictionary:
      classname, contents = self.__get_object_data(dictionary)
      result = self.__populate_classname_by_dict(classname, contents)
    else:
      result = None

    self._get_logger().debug(u'End mapping dictionary to object. Time elapsed {0}'.format(datetime.now() - start_time))
    return result

  def __get_object_data(self, dictionary):
    """ Returns the classname and the corresponding data"""
    self._get_logger().debug(u'Decapsulating dictionary to classname and data')
    if len(dictionary) == 1:
      for key, value in dictionary.iteritems():
        self._get_logger().debug(u'Found class name {0}'.format(key))
        return key, value
    else:
      raise DictConversionException(u'Dictionary is malformed expected one entry got more.')

  def __populate_classname_by_dict(self, classname, dictionary):
    """ Maps the data to the class"""
    self._get_logger().debug(u'Mapping dictionary to class {0}'.format(classname))
    instance = get_class(u'ce1sus.api.restclasses', classname)()
    if not isinstance(instance, RestClass):
      raise DictConversionException((u'{0} does not implement RestClass').format(classname))
    self.__populate_instance_by_dict(instance, dictionary)
    return instance

  def __set_dict_value(self, instance, key, value):
    """ Maps sub object"""
    self._get_logger().debug(u'Mapping sub object for attribute {0}'.format(key))
    subkey, subvalue = self.__get_object_data(value)
    subinstance = self.__populate_classname_by_dict(subkey, subvalue)
    setattr(instance, key, subinstance)

  def __set_list_value(self, instance, key, value):
    """ Maps the list attribute"""
    self._get_logger().debug(u'Mapping list for attribute {0}'.format(key))
    result = list()
    for item in value:
      # if dictionary then they are objects
      if isinstance(item, DictionaryType):
        subkey, subvalue = self.__get_object_data(item)
        subinstance = self.__populate_classname_by_dict(subkey, subvalue)
        result.append(subinstance)
      else:
        # its acutally a single value
        result = value
        break
    setattr(instance, key, result)

  def __populate_atomic_value(self, instance, key, value):
    """ Maps atomic attribute"""
    self._get_logger().debug(u'Mapping value "{1}" for attribute {0}'.format(key, value))
    if value == '':
      value = None
    else:
      string_value = u'{0}'.format(value)
      value = convert_string_to_value(string_value)
    setattr(instance, key, value)

  def __populate_instance_by_dict(self, instance, dictionary):
    """populates the instance with the dictinary values"""
    self._get_logger().debug(u'Populating instance by dictionary')
    for key, value in dictionary.iteritems():
      if isinstance(value, DictionaryType):
        self.__set_dict_value(instance, key, value)
      elif isinstance(value, ListType):
        self.__set_list_value(instance, key, value)
      else:
        self.__populate_atomic_value(instance, key, value)

  def convert_to_rest_obj(self, dictionary):
    """Maps a dictionary to an instance"""
    self._get_logger().debug(u'Mapping dictionary')
    instance = self.__map_dict_to_object(dictionary)
    return instance

  def convert_to_dict(self, rest_object):
    """converts an rest_object to a dictionary"""
    self._get_logger().debug(u'Converting {0} to dictionary'.format(rest_object.get_classname()))
    return rest_object.to_dict()
