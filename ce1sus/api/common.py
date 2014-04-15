# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 6, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from dagr.helpers.debug import Log
from json import JSONEncoder, JSONDecoder
from ce1sus.api.dictconverter import DictConverter, DictConversionException
import json
import decimal


class JSONException(Exception):
  """Base exception for this class"""
  pass


class JSONRequestFailedException(JSONException):
  """Base exception for this class"""
  pass


class JSONConverter(object):

  """Class used to map json to rest classes and vice versa"""

  @staticmethod
  def default(o):
    if isinstance(o, decimal.Decimal):
      return str(o)

  def __init__(self, config):
    self.logger = Log(config)
    self.__encoder = JSONEncoder()
    self.__dictconverter = DictConverter(config)

  def generate_json(self, dictionary):
    """encodes dictionary to JSON"""
    self._get_logger().debug(u'Encoding dictionary to JSON')
    return json.dumps(dictionary, default=JSONConverter.default)
    # return JSONEncoder().encode(dictionary)

  def decode_json(self, json):
    """decodes JSON to dictionary"""
    self._get_logger().debug(u'Decoding JSON to dictionary')
    return JSONDecoder().decode(json)

  def _get_logger(self):
    """Returns the class logger"""
    return self.logger.get_logger(self.__class__.__name__)

  def get_json(self, rest_object):
    """Converts the RestObject to JSON"""
    dictionary = rest_object.to_dict()
    return self.generate_json(dictionary)

  def __get_data(self, dictionary):
    self._get_logger().debug(u'Pharsing JSON answer')
    # get the answer if on the server went everything correct
    response = dictionary.pop('response', None)
    if response:
      status = response.get('status', None)
      if status == 'OK':
        # only the remaining stuff should be in the dictionary
        return dictionary
      else:
        message = response.get('errors', '')[0]
        raise JSONRequestFailedException(message)
    else:
      raise JSONException(u'Malformatted JSON')

  def get_rest_object(self, json_string):
    """Converts a JSON string to rest objects"""
    dictionary = self.decode_json(json_string)
    data = self.__get_data(dictionary)
    try:
      results = data.get('Results', None)
      if results is None:
        return self.__dictconverter.convert_to_rest_obj(data)
      else:
        rest_items = list()
        for item in results:
          rest_item = self.__dictconverter.convert_to_rest_obj(item)
          rest_items.append(rest_item)
        return rest_items

    except DictConversionException as error:
      self._get_logger().fatal(error)
      raise JSONException(error)
