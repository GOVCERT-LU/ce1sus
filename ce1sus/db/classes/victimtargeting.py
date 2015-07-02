# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 25, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, BigInteger

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import TLP, Properties
from ce1sus.db.classes.identity import Identity
from ce1sus.db.common.session import Base
from stix.common import vocabs


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_VICTIMTARGETING_IDENTITY = Table('rel_victimtargeting_identity', Base.metadata,
                                       Column('rti_id', BigInteger, primary_key=True, nullable=False, index=True),
                                       Column('victimtargeting_id', BigInteger, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                       Column('identity_id', BigInteger, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                                       )


class TargetedInformation(Base):
  type = Column('type', Integer, default=None)
  vt_id = Column(BigInteger, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: vocabs.InformationType.TERM_INFORMATION_ASSETS,
            1: vocabs.InformationType.TERM_INFORMATION_ASSETS_CORPORATE_EMPLOYEE_INFORMATION,
            2: vocabs.InformationType.TERM_INFORMATION_ASSETS_CUSTOMER_PII,
            3: vocabs.InformationType.TERM_INFORMATION_ASSETS_EMAIL_LISTS_OR_ARCHIVES,
            4: vocabs.InformationType.TERM_INFORMATION_ASSETS_FINANCIAL_DATA,
            5: vocabs.InformationType.TERM_INFORMATION_ASSETS_INTELLECTUAL_PROPERTY,
            6: vocabs.InformationType.TERM_INFORMATION_ASSETS_MOBILE_PHONE_CONTACTS,
            7: vocabs.InformationType.TERM_INFORMATION_ASSETS_USER_CREDENTIALS,
            8: vocabs.InformationType.TERM_AUTHENTICATION_COOKIES,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class TargetedSystems(Base):
  type = Column('type', Integer, default=None)
  vt_id = Column(BigInteger, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  @classmethod
  def get_dictionary(cls):
    return {
            0: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS,
            1: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_APPLICATION_LAYER,
            2: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_DATABASE_LAYER,
            3: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_ENTERPRISE_TECHNOLOGIES_AND_SUPPORT_INFRASTRUCTURE,
            4: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_NETWORK_SYSTEMS,
            5: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_NETWORKING_DEVICES,
            6: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_WEB_LAYER,
            7: vocabs.SystemType.TERM_ENTERPRISE_SYSTEMS_VOIP,
            8: vocabs.SystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS,
            9: vocabs.SystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_EQUIPMENT_UNDER_CONTROL,
            10: vocabs.SystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_OPERATIONS_MANAGEMENT,
            11: vocabs.SystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_SAFETY_PROTECTION_AND_LOCAL_CONTROL,
            12: vocabs.SystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_SUPERVISORY_CONTROL,
            13: vocabs.SystemType.TERM_MOBILE_SYSTEMS,
            14: vocabs.SystemType.TERM_MOBILE_SYSTEMS_MOBILE_OPERATING_SYSTEMS,
            15: vocabs.SystemType.TERM_MOBILE_SYSTEMS_NEAR_FIELD_COMMUNICATIONS,
            16: vocabs.SystemType.TERM_MOBILE_SYSTEMS_MOBILE_DEVICES,
            17: vocabs.SystemType.TERM_THIRDPARTY_SERVICES,
            18: vocabs.SystemType.TERM_THIRDPARTY_SERVICES_APPLICATION_STORES,
            19: vocabs.SystemType.TERM_THIRDPARTY_SERVICES_CLOUD_SERVICES,
            20: vocabs.SystemType.TERM_THIRDPARTY_SERVICES_SECURITY_VENDORS,
            21: vocabs.SystemType.TERM_THIRDPARTY_SERVICES_SOCIAL_MEDIA,
            22: vocabs.SystemType.TERM_THIRDPARTY_SERVICES_SOFTWARE_UPDATE,
            23: vocabs.SystemType.TERM_USERS,
            24: vocabs.SystemType.TERM_USERS_APPLICATION_AND_SOFTWARE,
            25: vocabs.SystemType.TERM_USERS_WORKSTATION,
            26: vocabs.SystemType.TERM_USERS_REMOVABLE_MEDIA,
            }

  @property
  def name(self):
    return self.get_dictionary().get(self.type, None)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'name': self.convert_value(self.name)}


class VictimTargeting(ExtendedLogingInformations, Base):
  identity = relationship(Identity, secondary='rel_victimtargeting_identity', uselist=False)
  targeted_systems = relationship(TargetedSystems)
  targeted_information = relationship(TargetedInformation)
  # TODO targeted_technical_details
  # targeted_technical_details = None

  # custom ones related to ce1sus internals
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  vulnerability_id = Column('vulnerability_id', BigInteger, ForeignKey('vulnerabilitys.vulnerability_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

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
