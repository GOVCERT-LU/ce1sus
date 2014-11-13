# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from datetime import datetime


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def set_properties(instance):
  instance.properties.is_rest_instert = True
  instance.properties.is_proposal = False
  instance.properties.is_web_insert = False
  instance.properties.is_validated = False
  instance.properties.is_shareable = True


def set_extended_logging(instance, user, group):
  if not instance.originating_group:
    instance.originating_group = group
  instance.creator_group = group
  set_simple_logging(instance, user)


def set_simple_logging(instance, user):
  if not instance.created_at:
    instance.created_at = datetime.utcnow()
  instance.modified_on = datetime.utcnow()
  instance.creator = user
  instance.modifier = user


def extract_uuid(stix_identifier):
  uuid = stix_identifier[-36:]
  return uuid


def make_dict_definitions(definitions):
  result = dict()
  for definition in definitions:
    result[definition.name] = definition
  return result
