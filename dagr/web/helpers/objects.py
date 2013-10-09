# -*- coding: utf-8 -*-

"""
module in charge of object foo, since cherrypy sends more parameters

Created Aug, 2013
"""
import copy


# pylint: disable=W0613
def copyObject(context, obj):
  """
  returns a copy of the obj
  """
  return copy.deepcopy(obj)
