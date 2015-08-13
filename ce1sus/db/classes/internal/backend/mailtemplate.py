# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from sqlalchemy.schema import Column

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.core import SimpleLogingInformations, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailTemplate(SimpleLogingInformations, Base):
  """This is a container class for the Mails table."""
  name = Column('name', UnicodeType(255), nullable=False)
  body = Column('body', UnicodeTextType(), nullable=False)
  subject = Column('subject', UnicodeType(255), nullable=False)

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'name': self.convert_value(self.name),
                'body': self.convert_value(self.body),
                'subject': self.convert_value(self.subject)
                }
    else:
      result = {'name': self.convert_value(self.name)}

    parent_dict = SimpleLogingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    """Validates the mail template object"""
    ObjectValidator.validateAlNum(self, 'name', withSpaces=True, minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'body',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self, 'subject', withSpaces=True, minLength=3,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)
