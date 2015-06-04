# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 20, 2014
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, UnicodeText

from ce1sus.db.classes.basedbobject import SimpleLogingInformations
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susConfig(SimpleLogingInformations, Base):
  key = Column('key', Unicode(255, collation='utf8_unicode_ci'), nullable=False, index=True)
  value = Column('value', UnicodeText(collation='utf8_unicode_ci'), nullable=False)

  def validate(self):
        # TODO: create validation for ce1susconfig
    """
    Returns true if the object is valid
    """
    return self
