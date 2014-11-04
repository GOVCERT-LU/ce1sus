# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Text

from ce1sus.db.classes.basedbobject import SimpleLogingInformations
from ce1sus.db.common.session import Base
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MailTemplate(SimpleLogingInformations, Base):
  """This is a container class for the Mails table."""
  name = Column('name', Unicode(255), nullable=False)
  body = Column('body', Text, nullable=False)
  subject = Column('subject', Unicode(255), nullable=False)

  def to_dict(self, complete=True):
    if complete:
      return {'identifier': self.convert_value(self.identifier),
              'name': self.convert_value(self.name),
              'body': self.convert_value(self.body),
              'subject': self.convert_value(self.subject)}
    else:
      return {'identifier': self.convert_value(self.identifier),
              'name': self.convert_value(self.name)}

  def populate(self, json):
    self.name = json.get('name', None)
    self.body = json.get('body', None)
    self.subject = json.get('subject', None)

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
