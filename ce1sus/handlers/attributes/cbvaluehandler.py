# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""
from ce1sus.db.classes.common import ValueTable
from ce1sus.handlers.base import HandlerException
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.helpers.common.validator.valuevalidator import ValueValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CBValueHandler(GenericHandler):
    """The generic handler for handling known atomic values"""

    @staticmethod
    def get_uuid():
        return '141dea70-8dec-11e3-baa8-0800200c9a66'

    @staticmethod
    def get_allowed_types():
        return [ValueTable.STRING_VALUE]

    @staticmethod
    def get_description():
        return u'CB Handler used for creating comboboxes. Note The REGEX defines the valies, therefore it must be under the format of: "^(?:\^.+\$\|)+(?:\^.+\$)$"'

    @staticmethod
    def __check_vailidity_regex(regex):
        """
        Checks if the regular expression is under the correct form
        """
        val_regex = r'^(?:\^.+\$\|)+(?:\^.+\$)$'
        valid = ValueValidator.validateRegex(regex,
                                             val_regex,
                                             '')
        if not valid:
            raise HandlerException(('The regular expression of the definition is invalid.\n'
                                    + 'It should be under the form of:\n{0}\n'
                                    + 'Please fix the definition before using this definition.'
                                    ).format(val_regex))

    @staticmethod
    def __get_cb_values(regex):
        """
        Returns the combo box values
        """
        result = list()
        CBValueHandler.__check_vailidity_regex(regex)
        items = regex.split('|')
        for item in items:
            temp = item.replace('$', '')
            temp = temp.replace('^', '')
            result.append(temp)
        return result

    def get_data(self, attribute, definition, parameters):
        regex = definition.regex
        if regex:
            cb_values = CBValueHandler.__get_cb_values(regex)
            result = list()
            for item in cb_values:
                result.append({'identifier': item, 'name': item})
            return result
        else:
            raise HandlerException(u'Troubles getting regex')

    def get_view_type(self):
        return 'combobox'
