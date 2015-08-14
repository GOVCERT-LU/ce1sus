# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
import re


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class VersionException(Exception):
  pass


class Version(object):

  def __init__(self, version=None, parentObj=None, attr_name='version_db'):
    self.__attr_name = attr_name
    self.__parent_object = parentObj
    if version:
      self.__version = version
    else:
      self.__version = '0.0.0'
    if self.__parent_object:
      setattr(parentObj, attr_name, self.__version)

  def get_classname(self):
    return self.__class__.__name__

  @property
  def uuid(self):
    if self.__parent_object:
      return self.__parent_object.uuid
    return None

  @property
  def version(self):
    if self.__parent_object:
      return getattr(self.__parent_object, self.__attr_name)
    else:
      return self.__version

  @version.setter
  def version(self, version):
    if isinstance(version, Version):
      version_str = version.version
    else:
      version_str = version
    if len(version_str.split('.')) == 3:
      if self.__parent_object:
        setattr(self.__parent_object, self.__attr_name, version_str)
      self.__version = version_str
    else:
      raise VersionException()

  def compare(self, version):
    """
        returns 1 : version >
        returns 0 : version =
        returns -1: version -<
    """

    if isinstance(version, Version):
      version_str = version.version
    else:
      version_str = version

    def normalize(v):
      return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

    return cmp(normalize(self.__version), normalize(version_str)) * -1

  def parse(self, version=None):
    if version:
      int_version = version
    else:
      int_version = self.version
    array = int_version.split('.')
    if len(array) == 3:
      return int(array[0]), int(array[1]), int(array[2]),
    else:
      raise VersionException()

  def increase_minor(self):
    major, minor, patch = self.parse()
    minor = minor + 1
    self.version = '{0}.{1}.{2}'.format(major, minor, patch)

  def increase_major(self):
    major, minor, patch = self.parse()
    major = major + 1
    self.version = '{0}.{1}.{2}'.format(major, minor, patch)

  def increase_patch(self):
    major, minor, patch = self.parse()
    patch = patch + 1
    self.version = '{0}.{1}.{2}'.format(major, minor, patch)


  def add(self, version):
    if isinstance(version, Version):
      version_str = version.version
    else:
      version_str = version
    major, minor, patch = self.parse()
    major2, minor2, patch2 = self.parse(version_str)
    self.version = '{0}.{1}.{2}'.format(major + major2, minor + minor2, patch + patch2)

  def __str__(self):
    return self.__version
