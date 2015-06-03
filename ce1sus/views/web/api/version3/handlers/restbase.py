# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 5, 2014
"""

import re

from ce1sus.controllers.common.assembler import Assembler
from ce1sus.views.web.common.base import BaseView
from ce1sus.handlers.base import HandlerException
from ce1sus.controllers.base import BaseController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

ALLOWED_HTTP_METHODS = ['GET', 'PUT', 'POST', 'DELETE']


def valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


def rest_method(**kwargs):

    default = kwargs.get('default', False)

    # TODO: check if the method has the right amount of arguments and the right ones
    def decorate(method):
        method.rest_method = True
        method.default_fct = default
        return method

    return decorate


def methods(**kwargs):
    # TODO: check if the method has the right amount of arguments and the right ones
    allowed = kwargs.get('allowed', list())

    def decorate(method):

        if not isinstance(allowed, list):
            raise RestHandlerException(u'Allowed methods for function {0} has to be an array'.format(method.__name__))
        else:
            method.allowed_http_methods = allowed
        return method

    return decorate


def require(*conditions):

    def decorate(method):
        method.require_auth_flag = True
        method.require_auth = list()
        if conditions:
            method.require_auth.extend(conditions)
        return method

    return decorate


class RestHandlerException(Exception):
    """
    Exception base for handler exceptions
    """
    pass


class PathParsingException(RestHandlerException):
    pass


class RestHandlerNotFoundException(RestHandlerException):
    """
    Exception base for handler exceptions
    """
    pass


class RestBaseHandler(BaseView):
    """Base class for handlers"""

    controllers = dict()

    def __init__(self, config):
        BaseView.__init__(self, config)
        self.assembler = Assembler(config)

    def controller_factory(self, clazz):
        if issubclass(clazz, BaseController):
            classname = clazz.__name__
            if classname in RestBaseHandler.controllers:
                return RestBaseHandler.controllers[classname]
            # need to create the broker
            self.logger.debug('Create controller for {0}'.format(clazz))
            instance = clazz(self.config)
            RestBaseHandler.controllers[classname] = instance
            return instance
        else:
            raise HandlerException('Class does not implement BaseController')

    @property
    def name(self):
        return self.__class__.__name__

    def get_detail_value(self, args):
        parameters = args.get('parameters')
        details = parameters.get('complete', 'false')
        if details == 'true':
            details = True
        else:
            details = False
        return details

    def get_inflated_value(self, args):
        parameters = args.get('parameters')
        inflated = parameters.get('inflated', 'false')
        if inflated == 'true':
            inflated = True
        else:
            inflated = False
        return inflated

    def get_flat_value(self, args):
        parameters = args.get('parameters')
        flat = parameters.get('flat', 'false')
        if flat == 'true':
            flat = True
        else:
            flat = False
        return flat

    def parse_path(self, path, method):
        """
        the path can either be empty or belongs to one of the following structures
        uuid/observable
        uuid/composed_observable
        uuid/object
        uuid/attribute

        uuid/observable/uuid
        uuid/composed_observable/uuid
        uuid/object/uuid
        uuid/attribute/uuid

        Everything else will be ignored
        """
        result = {'event_id': None,  # uuid of the event
                  'object_type': None,
                  'object_uuid': None,
                  'sub_object': None
                  }
        if len(path) > 0:
            event_id = path.pop(0)
            if valid_uuid(event_id):
                result['event_id'] = event_id
            else:
                raise PathParsingException(u'{0} is not a valid uuid'.format(event_id))
            if len(path) > 0:
                object_type = path.pop(0)
                result['object_type'] = object_type
            if len(path) > 0:
                object_uuid = path.pop(0)
                if valid_uuid(object_uuid):
                    result['object_uuid'] = object_uuid
                else:
                    raise PathParsingException(u'{0} is not a valid uuid'.format(object_uuid))
            if len(path) > 0:
                if method == 'POST':
                    # can only be used for post to elements
                    sub_object = path.pop(0)
                    result['sub_object'] = sub_object
                else:
                    raise PathParsingException(u'Path is too long')
            if len(path) > 0:
                raise PathParsingException(u'Path is too long')
        return result

    def is_rest_insert(self, headers):
        webinsert = headers.get('frontend', None)
        if webinsert:
            return False
        else:
            return True
