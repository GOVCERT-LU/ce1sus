# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.helpers.handlers.generichandler import GenericHandler
from dagr.helpers.validator.valuevalidator import ValueValidator


class CBValueHandler(GenericHandler):
  """The generic handler for handling known atomic values"""
  def __init__(self):
    GenericHandler.__init__(self)

  def render(self, enabled, eventID, enableShare, user, definition, attribute=None):
    template = (self.
                getTemplate('/events/event/attributes/handlers/cbValues.html')
                )
    # create CB Values
    regex = self.definition.regex
    # validate regex else show error!
    valRegex = '^(?:\^.+\$\|)+(?:\^.+\$)$'
    result = ValueValidator.validateRegex(regex,
                                          valRegex,
                                          'errorMsg')

    cbValues = dict()
    if result:
      items = regex.split('|')
      for item in items:
        temp = item.replace('$', ' ')
        temp = temp.replace('^', ' ')
        cbValues[temp] = temp
        validationMsg = None
    else:
      validationMsg = ('The regular expression of the definition is invalid.'
                       + '<br/> It should be under the form of:<br/><b>'
                       + '{0}</b><br/>'
                  + 'Please fix the definition before using.').format(valRegex)
    if definition.share:
      defaultShareValue = 1
    else:
      defaultShareValue = 0
    string = template.render(attribute=attribute,
                             cbValues=cbValues,
                             enabled=enabled,
                             validationMsg=validationMsg,
                             defaultShareValue=defaultShareValue,
                             enableShare=enableShare)
    return string
