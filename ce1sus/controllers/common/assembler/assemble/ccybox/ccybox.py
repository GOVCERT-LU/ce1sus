# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from ce1sus.controllers.common.assembler.assemble.ccybox.pseudo import PseudoCyboxAssembler
from ce1sus.controllers.common.assembler.base import BaseAssembler
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition, ObservableKeyword


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CyboxAssembler(BaseAssembler):

  def __init__(self, config, session=None):
    super(CyboxAssembler, self).__init__(config, session)
    self.pseudo_assembler = self.controller_factory(PseudoCyboxAssembler)
    
  def assemble_observable(self, parent, json, cache_object):

    if json:
      observable = Observable()
      self.set_base(observable, json, cache_object, parent)
      observable.parent = parent

      observable.id_ = json.get('id_', None)
      observable.idref = json.get('idref', None)
      if not observable.idref:
        observable.title = json.get('title', None)
        description = json.get('description', None)
        if description:
          description = self.assemble_structured_text(observable, description, cache_object)
          # must be done to prevent multiple entries in the relations table
          description.observable_description = None
          observable.description = description

        obj = json.get('object', None)
        if obj:
          obj_def = obj.get('definition', None)
          if obj_def is None:
            obj_def = obj.get('definition_id', None)
          if obj_def:
            obj = self.pseudo_assembler.assemble_object(observable, obj, cache_object)
            if obj:

              # must be done to prevent multiple entries in the relations table
              observable.object = obj

        if not observable.object:
          observable_composition = json.get('observable_composition', None)
          if observable_composition:
            observable.observable_composition = self.assemble_observable_composition(observable, observable_composition, cache_object)

        observable.sighting_count = json.get('sighting_count', None)

        keywords = json.get('keywords', None)
        if keywords:
          for keyword in keywords:
            keyword = self.assemble_keyword(observable, keyword, cache_object)
            if keyword:
              observable.keywords.append(keyword)
          
        return observable

  def assemble_observable_composition(self, parent, json, cache_object):
    if json:
      composed = ObservableComposition()
      composed.parent = parent
      self.set_base(composed, json, cache_object, parent)
      composed.operator = json.get('operator', 'OR')
      observables = json.get('observables', None)
      if observables:
        for observable in observables:
          obs = self.assemble_observable(composed, observable, cache_object)
          if obs:
            composed.observables.append(obs)

      if composed.observables:
        return composed

  def assemble_keyword(self, observable, json, cache_object):
    keyword = ObservableKeyword()
    self.set_base(keyword, json, cache_object, observable)
    keyword.observable = observable
    keyword.keyword = json.get('keyword', None)
    if keyword.keyword:
      return keyword

  def assemble_object(self, observable, json, cache_object):
    return self.pseudo_assembler.assemble_object(observable, json, cache_object)

  def assemble_related_object(self, obj, json, cache_object):
    return self.pseudo_assembler.assemble_related_object(obj, json, cache_object)

  def assemble_attribute(self, obj, json, cache_object):
    return self.pseudo_assembler.assemble_attribute(obj, json, cache_object)
