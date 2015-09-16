# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 30, 2015
"""
from base64 import b64decode
from lxml import etree
from lxml.etree import ETCompatXMLParser

from ce1sus.common.classes.cacheobject import MergerCache
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.handlers.base import HandlerException
from ce1sus.mappers.stix.stixmapper import STIXConverter
from ce1sus.views.web.api.version3.handlers.adapters.base import AdapterHandlerBase
from ce1sus.views.web.api.version3.handlers.restbase import rest_method, methods, require, RestHandlerNotFoundException, RestHandlerException
from cybox.core import Observables
from openioc import get_root_tag, IocTermList
import openioc_to_cybox
from stix.core import STIXPackage, STIXHeader
from stix.indicator import Indicator
import stix.utils


__VERSION__ = 0.13


class OpenIOCHandler(AdapterHandlerBase):

  def __init__(self, config):
    super(OpenIOCHandler, self).__init__(config)
    self.dump = self.adapter_config.get('OpenIOCMapper', 'dump', False)
    self.dump_location = self.adapter_config.get('OpenIOCMapper', 'path', False)
    self.group_uuid = self.adapter_config.get('OpenIOCMapper', 'transformergroup', None)
    self.stix_converter = STIXConverter(config)

  @rest_method(default=True)
  @methods(allowed=['POST'])
  @require()
  def upload_xml(self, **args):
    try:
      cache_object = self.get_cache_object(args)
      cache_object.event_permissions = EventPermissions('0')
      cache_object.event_permissions.set_all()
      json = args.get('json')

      # check if the json is as expected
      filename = json.get('name', None)
      if filename:
        if 'XML' in filename or 'xml' in filename:
          data = json.get('data', None)
          if data:
            if data.get('data', None):
              data = data['data']
          else:
            raise HandlerException('Provided json does not have a data attribute')
        else:
          raise HandlerException('File does not end in xml or XML')
      else:
        raise HandlerException('Provided json does not have a file attribute')

      # start conversion
      xml_string = b64decode(data)
      if self.dump:
        self.dump_file(filename, data)

      xml_string = self.__make_stix_xml_string(filename, xml_string)
      f = open('/home/jhemp/f.xml', 'w+')
      f.write(xml_string)
      f.close()
      event = self.stix_converter.convert_stix_xml_string(xml_string, cache_object)
      cache_object_copy = cache_object.make_copy()
      cache_object_copy.complete = True
      cache_object_copy.inflated = True
      json_str = event.to_dict(cache_object_copy)

      event = self.assembler.assemble(json_str, Event, None, cache_object)

      try:
        db_event = self.event_controller.get_event_by_uuid(event.uuid)
        self.logger.debug('Event {0} is in db merging'.format(event.uuid))
        # present in db merge it
        cache_object.reset()
        merger_cache = MergerCache(cache_object)
        self.merger.merge(db_event, event, merger_cache)
        return db_event.to_dict(merger_cache)

      except ControllerNothingFoundException:
        self.logger.debug('Event {0} is not in db inserting'.format(event.uuid))
        # not present in db add it
        self.event_controller.insert_event(event, cache_object, True, True)
        return event.to_dict(cache_object)

    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)


  def __make_stix_xml_string(self, open_ioc_filename, xml_string):
    rootNode = etree.fromstring(xml_string, parser=ETCompatXMLParser())

    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ioctermlist'
        rootClass = IocTermList
    openioc_indicators = rootClass.factory()
    openioc_indicators.build(rootNode)

    observables_obj = openioc_to_cybox.generate_cybox(openioc_indicators, open_ioc_filename, True)
    observables_cls = Observables.from_obj(observables_obj)
    stix.utils.set_id_namespace({"https://github.com/STIXProject/openioc-to-stix": "openiocToSTIX"})
    stix_package = STIXPackage()
    stix_package.version = '1.1.1'
    input_namespaces = {"openioc": "http://openioc.org/"}

    stix_package.__input_namespaces__ = input_namespaces

    for observable in observables_cls.observables:
      indicator_dict = {}
      producer_dict = {}
      producer_dict['tools'] = [{'name': 'OpenIOC to STIX Utility', 'version': str(__VERSION__)}]
      indicator_dict['producer'] = producer_dict
      indicator_dict['title'] = "CybOX-represented Indicator Created from OpenIOC File"
      indicator = Indicator.from_dict(indicator_dict)
      indicator.add_observable(observables_cls.observables[0])
      stix_package.add_indicator(indicator)

    stix_header = STIXHeader()

    for child in rootNode:

      if  child.tag.endswith('short_description'):
        stix_header.short_description = child.text
      elif child.tag.endswith('description'):
        stix_header.description = child.text
      else:
        if stix_header.description and stix_header.short_description:
          break

    stix_header.package_intent = "Indicators - Malware Artifacts"
    stix_header.description = '{0}\n\n CybOX-represented Indicators Translated from OpenIOC File'.format(stix_header.description)
    stix_header.title = 'OpenIOC of file {0}'.format(open_ioc_filename)
    stix_package.stix_header = stix_header

    return stix_package.to_xml()

