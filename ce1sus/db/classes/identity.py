# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 26, 2015
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, Integer

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import TLP, Properties
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Identity(ExtendedLogingInformations, Base):
  """NOTE this is not used to represent information provides etc only for internal representations"""

  name = Column('name', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)

  # TODO: related_identities
  # related_identities = None

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """

    return TLP.get_by_id(self.tlp_level_id)

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.tlp_level_id = TLP.get_by_value(text)

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code
