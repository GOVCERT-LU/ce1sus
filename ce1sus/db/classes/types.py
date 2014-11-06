# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 6, 2014
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Integer, Text

from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeType(Base):

  name = Column('name', Unicode(255), nullable=False, index=True)
  table_id = Column('table_id', Integer(1), index=True)
  description = Column('description', Text)

  def validate(self):
    # TODO: Add validation
    return True


class AttributeViewType(Base):

  name = Column('name', Unicode(255), nullable=False, index=True)
  description = Column('description', Text)

  def validate(self):
    # TODO: Add validation
    return True
