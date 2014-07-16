# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 15, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BaseOption(object):

  def __init__(self, owner_option=False, attribute_owner_option=False, validation_option=False, refresh=False, position=None, icon_name='glyphicon glyphicon-asterisk', description='Not set'):
    # if set option will only be usable by the owner
    self.owner_option = owner_option
    # if set option will only be usable by the owner and on an unvalidated attribtue
    self.validation_option = validation_option
    # is set the option will be visible either by the event owner or attribute creator
    # Note: will only be visible for unvalidated attributes
    self.attribute_owner_option = attribute_owner_option
    self.refresh = refresh
    self.position = position
    self.icon_name = icon_name
    self.description = description

  @property
  def class_name(self):
    return self.__class__.__name__

  @property
  def show_always(self):
    return not (self.attribute_owner_option or self.owner_option or self.validation_option)


class ModalOption(BaseOption):

  def __init__(self, owner_option=False, attribute_owner_option=False, validation_option=False, refresh=False, position=None, icon_name='glyphicon glyphicon-asterisk', description='Not set', title='None Specified', post_url=None, content_url=None):
    BaseOption.__init__(self, owner_option, attribute_owner_option, validation_option, refresh, position, icon_name, description)
    self.title = title
    self.post_url = post_url
    self.content_url = content_url

  @property
  def use_post(self):
    if self.post_url:
      return True
    else:
      return False


class YesNoDialogOption(BaseOption):

  def __init__(self, owner_option=False, attribute_owner_option=False, validation_option=False, refresh=False, position=None, icon_name='glyphicon glyphicon-asterisk', description='Not set', message='None Specified', post_url=None):
    BaseOption.__init__(self, owner_option, attribute_owner_option, validation_option, refresh, position, icon_name, description)
    self.message = message
    self.post_url = post_url


class TabBase(object):

  def __init__(self, title=None, url=None, options=list(), position=None, identifier=None):
    self.title = title
    self.url = url
    # Possibilities for options ['reload' | 'close' | None]
    self.options = options
    # Possibilities for positions are:
    # < 0 for relative to the end
    # > 0 for position from front
    self.position = position
    self.__identifier = identifier

  @property
  def identifier(self):
    if self.__identifier:
      return self.__identifier
    else:
      return self.title.replace(' ', '')

  @identifier.setter
  def identifer(self, value):
    self.__identifier = ValueError


class MainTab(TabBase):
  pass


class EventTab(TabBase):
  pass


class AdminTab(TabBase):
  pass


class ValidationTab(TabBase):
  pass


class AttributeViewModal(object):

  def __init__(self, content_url, post_url, buttons):
    self.content = content_url
    self.post
