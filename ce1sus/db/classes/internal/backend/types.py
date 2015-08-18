# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 6, 2014
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.common import ValueTable
from ce1sus.db.classes.internal.corebase import BaseObject, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttributeType(BaseObject, Base):

  name = Column('name', UnicodeType(255), nullable=False, index=True, unique=True)
  table_id = Column('table_id', Integer, index=True)
  description = Column('description', UnicodeTextType())

  def validate(self):
        # TODO: Add validation
    return True


  def to_dict(self, cache_object):
    if self.table_id:
      name = ValueTable.get_by_id(self.table_id)
    else:
      name = 'Any'
    allowed_table = {'identifier': self.table_id, 'name': name}
    result = {'description': self.convert_value(self.description),
            'name': self.convert_value(self.name),
            'allowed_table': allowed_table
            }

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
