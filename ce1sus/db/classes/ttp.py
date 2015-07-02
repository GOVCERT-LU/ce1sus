from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import BigInteger, Integer, Unicode, UnicodeText

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Marking, TLP, Properties, IntendedEffect
from ce1sus.db.classes.identity import Identity
from ce1sus.db.common.session import Base
from stix.common import vocabs


_REL_TTP_TTPS = Table('rel_ttp_ttp', Base.metadata,
                             Column('rtt_id', BigInteger, primary_key=True, nullable=False, index=True),
                             Column('pttp_id', BigInteger, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                             Column('cttps_id', BigInteger, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                             )

_REL_INDICATOR_HANDLING = Table('rel_ttp_handling', Base.metadata,
                                Column('rth_id', BigInteger, primary_key=True, nullable=False, index=True),
                                Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                Column('marking_id', BigInteger, ForeignKey('markings.marking_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                )

_REL_TTP_KILLCHAINPHASE = Table('rel_ttp_killchainphase', Base.metadata,
                                      Column('rik_id', BigInteger, primary_key=True, nullable=False, index=True),
                                      Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                      Column('killchainphase_id', BigInteger, ForeignKey('killchainphases.killchainphase_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                      )

_REL_TTP_KILLCHAIN = Table('rel_ttp_killchain', Base.metadata,
                                       Column('rtk_id', BigInteger, primary_key=True, nullable=False, index=True),
                                       Column('killchain_id', BigInteger, ForeignKey('killchains.killchain_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                       Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                       )

_REL_TTPRESOURCE_IDENTITY = Table('rel_ttpresource_identity', Base.metadata,
                                       Column('rti_id', BigInteger, primary_key=True, nullable=False, index=True),
                                       Column('ttpresource_id', BigInteger, ForeignKey('ttpresources.ttpresource_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                       Column('identity_id', BigInteger, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                       )

_REL_TTP_INTENDEDEFFECT = Table('rel_ttp_intendedeffect', Base.metadata,
                                     Column('rti_id', BigInteger, primary_key=True, nullable=False, index=True),
                                     Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True),
                                     Column('intendedeffect_id', BigInteger, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                     )


class InfraStructureType(Base):

  type = Column('type', Integer, default=None, nullable=False)
  ttp_id = Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @classmethod
  def get_dictionary(cls):
    return {
            0: vocabs.AttackerInfrastructureType.TERM_ANONYMIZATION,
            1: vocabs.AttackerInfrastructureType.TERM_ANONYMIZATION_PROXY,
            2: vocabs.AttackerInfrastructureType.TERM_ANONYMIZATION_TOR_NETWORK,
            3: vocabs.AttackerInfrastructureType.TERM_ANONYMIZATION_VPN,
            4: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS,
            5: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_BLOGS,
            6: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_FORUMS,
            7: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_INTERNET_RELAY_CHAT,
            8: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_MICROBLOGS,
            9: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_MOBILE_COMMUNICATIONS,
            10: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_SOCIAL_NETWORKS,
            11: vocabs.AttackerInfrastructureType.TERM_COMMUNICATIONS_USERGENERATED_CONTENT_WEBSITES,
            12: vocabs.AttackerInfrastructureType.TERM_DOMAIN_REGISTRATION,
            13: vocabs.AttackerInfrastructureType.TERM_DOMAIN_REGISTRATION_DYNAMIC_DNS_SERVICES,
            14: vocabs.AttackerInfrastructureType.TERM_DOMAIN_REGISTRATION_LEGITIMATE_DOMAIN_REGISTRATION_SERVICES,
            15: vocabs.AttackerInfrastructureType.TERM_DOMAIN_REGISTRATION_MALICIOUS_DOMAIN_REGISTRARS,
            16: vocabs.AttackerInfrastructureType.TERM_DOMAIN_REGISTRATION_TOPLEVEL_DOMAIN_REGISTRARS,
            17: vocabs.AttackerInfrastructureType.TERM_HOSTING,
            18: vocabs.AttackerInfrastructureType.TERM_HOSTING_BULLETPROOF_OR_ROGUE_HOSTING,
            19: vocabs.AttackerInfrastructureType.TERM_HOSTING_CLOUD_HOSTING,
            20: vocabs.AttackerInfrastructureType.TERM_HOSTING_COMPROMISED_SERVER,
            21: vocabs.AttackerInfrastructureType.TERM_HOSTING_FAST_FLUX_BOTNET_HOSTING,
            22: vocabs.AttackerInfrastructureType.TERM_HOSTING_LEGITIMATE_HOSTING,
            23: vocabs.AttackerInfrastructureType.TERM_ELECTRONIC_PAYMENT_METHODS,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}

class Infrastructure(ExtendedLogingInformations, Base):

  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  ttp = relationship('TTP', uselist=False)
  ttp_id = Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

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

class ToolInformation(ExtendedLogingInformations, Base):

  tool_name = Column('tool_name', Unicode(255, collation='utf8_unicode_ci'))
  tool_vendor = Column('tool_vendor', Unicode(255, collation='utf8_unicode_ci'))
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  ttp = relationship('TTP', uselist=False)
  ttp_id = Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

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

class TTPResource(ExtendedLogingInformations, Base):

  tools = relationship(ToolInformation)
  Infrastructure = relationship(Infrastructure, uselist=False)
  personas = relationship(Identity, secondary='rel_ttpresource_identity')

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  ttp = relationship('TTP', uselist=False)
  ttp_id = Column('ttp_id', BigInteger, ForeignKey('ttps.ttp_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

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


class TTP(ExtendedLogingInformations, Base):

  # base properties
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  short_description = Column('short_description', Unicode(255, collation='utf8_unicode_ci'))
  version = Column('version', Unicode(40, collation='utf8_unicode_ci'), default=u'1.0.0', nullable=False)
  handling = relationship(Marking, secondary='rel_ttp_handling')

  behavior = relationship('Behavior', uselist=False)
  # TODO: related TTPs
  # related_ttps = None

  intended_effects = relationship(IntendedEffect, secondary='rel_ttp_intendedeffect')
  resources = relationship('TTPResource', uselist=False)
  victim_targeting = relationship('VictimTargeting')

  # TODO: in the xsd but not in the python-stix
  # killchainphases = relationship('KillChainPhase', secondary='rel_ttp_killchainphase')
  # killchains = relationship('Killchain', secondary='rel_ttp_killchain')


  exploit_targets = relationship('RelatedExploitTargets', uselist=False)

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

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
