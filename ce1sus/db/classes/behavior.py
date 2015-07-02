# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 25, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, BigInteger, Integer

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.common.session import Base
from stix.common import vocabs


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class MalwareInstance(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  behavior_id = Column('behavior_id', BigInteger, ForeignKey('behaviors.behavior_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  names = relationship('MalwareName')
  types = relationship('MalwareType')

class MalwareName(Base):
  name = Column('name', Unicode(255, collation='utf8_unicode_ci'), default=None)
  mt_id = Column(BigInteger, ForeignKey('malwareinstances.malwareinstance_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)


class MalwareType(Base):
  type = Column('type', Integer, default=None)
  mt_id = Column(BigInteger, ForeignKey('malwareinstances.malwareinstance_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: vocabs.MalwareType.TERM_AUTOMATED_TRANSFER_SCRIPTS,
            1: vocabs.MalwareType.TERM_ADWARE,
            2: vocabs.MalwareType.TERM_DIALER,
            3: vocabs.MalwareType.TERM_BOT,
            4: vocabs.MalwareType.TERM_BOT_CREDENTIAL_THEFT,
            5: vocabs.MalwareType.TERM_BOT_DDOS,
            6: vocabs.MalwareType.TERM_BOT_LOADER ,
            7: vocabs.MalwareType.TERM_BOT_SPAM,
            8: vocabs.MalwareType.TERM_DOS_OR_DDOS,
            9: vocabs.MalwareType.TERM_DOS_OR_DDOS_PARTICIPATORY,
            10: vocabs.MalwareType.TERM_DOS_OR_DDOS_SCRIPT,
            11: vocabs.MalwareType.TERM_DOS_OR_DDOS_STRESS_TEST_TOOLS ,
            12: vocabs.MalwareType.TERM_EXPLOIT_KITS,
            13: vocabs.MalwareType.TERM_POS_OR_ATM_MALWARE ,
            14: vocabs.MalwareType.TERM_RANSOMWARE ,
            15: vocabs.MalwareType.TERM_REMOTE_ACCESS_TROJAN ,
            16: vocabs.MalwareType.TERM_ROGUE_ANTIVIRUS ,
            17: vocabs.MalwareType.TERM_ROOTKIT
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}

class AttackPattern(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  behavior_id = Column('behavior_id', BigInteger, ForeignKey('behaviors.behavior_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

class Exploit(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  behavior_id = Column('behavior_id', BigInteger, ForeignKey('behaviors.behavior_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

class Behavior(ExtendedLogingInformations, Base):
  ttp_id = Column(BigInteger, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  malware_instances = relationship(MalwareInstance)
  attack_patterns = relationship(AttackPattern)
  exploits = relationship(Exploit)
