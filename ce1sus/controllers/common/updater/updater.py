# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from sqlalchemy.orm.session import make_transient

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.controllers.common.merger.merger import Merger
from ce1sus.common.classes.cacheobject import MergerCache


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Updater(BaseController):

  def __init__(self, config, session=None):
    super(Updater, self).__init__(config, session)
    self.assembler = self.controller_factory(Assembler)
    self.merger = self.controller_factory(Merger)

  def update(self, instance, json, cache_object):
    cache_object.insert = False
    classname = instance.get_classname()
    self.logger.debug('Updating {0}'.format(classname))

    if hasattr(instance, 'parent'):
      parent = instance.parent
      if parent:
        if hasattr(parent, 'definition'):
          parent.definition.attributes
        make_transient(parent)
        pass
    else:
      parent = None
    new_instance = self.assembler.assemble(json, instance.__class__, parent, cache_object)
    # Reset cache object
    cache_object.reset()
    merger_cache = MergerCache(cache_object)
    if isinstance(new_instance, list):
      new_instance = new_instance[0]
    version = self.merger.merge(instance, new_instance, merger_cache)
    merger_cache.version.version = version.version
    if parent:
      # This is done so that the transient object will also be updated
      obj = self.attr_def_broker.session.query(parent.__class__).filter(parent.__class__.identifier == parent.identifier).one()
      self.merger.cybox_merger.set_base(obj, parent, merger_cache)
    return version
