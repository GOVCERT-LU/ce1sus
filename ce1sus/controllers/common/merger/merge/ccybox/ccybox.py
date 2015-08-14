# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger
from ce1sus.controllers.common.merger.merge.ccybox.pseudo import PseudoCyboxMerger
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CyboxMerger(BaseMerger):

  def __init__(self, config, session=None):
    super(CyboxMerger, self).__init__(config, session)
    self.pseudo_cybox_merger = PseudoCyboxMerger(config, session)

  def merge_observables(self, old_instance, new_instance, cache_object):
    return self.merge_gen_arrays(old_instance, new_instance, cache_object, self.merge_observable)

  def merge_observable(self, old_instance, new_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'id_', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'title', cache_object))
      version.add(self.merge_structured_text(old_instance.description, new_instance.description, cache_object))

      version.add(self.pseudo_cybox_merger.merge_object(old_instance.object, new_instance.object, cache_object))
      version.add(self.merge_observable_composition(old_instance.observable_composition, new_instance.observable_composition, cache_object))

      version.add(self.update_instance_value(old_instance, new_instance, 'idref', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'sighting_count', cache_object))

      version.add(self.merge_keywords(old_instance.keywords, new_instance.keywords, cache_object))


    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)

      # Update also event
      self.set_base(old_instance.event[0], None, cache_object)

    return version

  def merge_observable_composition(self, old_instance, new_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'operator', cache_object))
      version.add(self.merge_observables(old_instance.observables, new_instance.observables, cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)

      # Update also event
      self.set_base(old_instance.event, None, cache_object)

    return version

  def merge_keywords(self, old_instance, new_instance, cache_object):
    return self.merge_gen_arrays(old_instance, new_instance, cache_object, self.merge_keyword)

  def merge_keyword(self, old_instance, new_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'keyword', cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)

      # Update also event
      self.set_base(old_instance.observable.event, None, cache_object)
    return version
