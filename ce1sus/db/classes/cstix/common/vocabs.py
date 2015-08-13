# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""


from ce1sus.db.classes.common.basevocab import BaseVocab
from stix.common.vocabs import AssetType as StixAssetType
from stix.common.vocabs import AvailabilityLossType as StixAvailabilityLossType
from stix.common.vocabs import COAStage as StixCOAStage
from stix.common.vocabs import CampaignStatus as StixCampaignStatus
from stix.common.vocabs import CourseOfActionType as StixCourseOfActionType
from stix.common.vocabs import DiscoveryMethod as StixDiscoveryMethod
from stix.common.vocabs import HighMediumLow as StixHighMediumLow
from stix.common.vocabs import ImpactQualification as StixImpactQualification
from stix.common.vocabs import ImpactRating as StixImpactRating
from stix.common.vocabs import IncidentCategory as StixIncidentCategory
from stix.common.vocabs import IncidentEffect as StixIncidentEffect
from stix.common.vocabs import IncidentStatus as StixIncidentStatus
from stix.common.vocabs import IndicatorType as StixIndicatorType
from stix.common.vocabs import InformationSourceRole as StixInformationSourceRole
from stix.common.vocabs import InformationType as StixInformationType
from stix.common.vocabs import IntendedEffect as StixIntendedEffect
from stix.common.vocabs import LocationClass as StixLocationClass
from stix.common.vocabs import LossDuration as StixLossDuration
from stix.common.vocabs import LossProperty as StixLossProperty
from stix.common.vocabs import MalwareType as StixMalwareType
from stix.common.vocabs import ManagementClass as StixManagementClass
from stix.common.vocabs import Motivation as StixMotivation
from stix.common.vocabs import OwnershipClass as StixOwnershipClass
from stix.common.vocabs import PackageIntent as StixPackageIntent
from stix.common.vocabs import PlanningAndOperationalSupport as StixPlanningAndOperationalSupport
from stix.common.vocabs import SecurityCompromise as StixSecurityCompromise
from stix.common.vocabs import SystemType as StixSystemType
from stix.common.vocabs import ThreatActorSophistication as StixThreatActorSophistication
from stix.common.vocabs import ThreatActorType as StixThreatActorType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ImpactRating(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            1: StixImpactRating.TERM_NONE,
            2: StixImpactRating.TERM_MINOR,
            3: StixImpactRating.TERM_MODERATE,
            4: StixImpactRating.TERM_MAJOR,
            5: StixImpactRating.TERM_UNKNOWN,
            }


class CampaignStatus(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {1: StixCampaignStatus.TERM_ONGOING,
            2: StixCampaignStatus.TERM_HISTORIC,
            3: StixCampaignStatus.TERM_FUTURE}


class IncidentEffect(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            1: StixIncidentEffect.TERM_BRAND_OR_IMAGE_DEGRADATION,
            2: StixIncidentEffect.TERM_LOSS_OF_COMPETITIVE_ADVANTAGE,
            3: StixIncidentEffect.TERM_LOSS_OF_COMPETITIVE_ADVANTAGE_ECONOMIC,
            4: StixIncidentEffect.TERM_LOSS_OF_COMPETITIVE_ADVANTAGE_MILITARY,
            5: StixIncidentEffect.TERM_LOSS_OF_COMPETITIVE_ADVANTAGE_POLITICAL,
            6: StixIncidentEffect.TERM_DATA_BREACH_OR_COMPROMISE,
            7: StixIncidentEffect.TERM_DEGRADATION_OF_SERVICE,
            8: StixIncidentEffect.TERM_DESTRUCTION,
            9: StixIncidentEffect.TERM_DISRUPTION_OF_SERVICE_OR_OPERATIONS,
            10: StixIncidentEffect.TERM_FINANCIAL_LOSS,
            11: StixIncidentEffect.TERM_LOSS_OF_CONFIDENTIAL_OR_PROPRIETARY_INFORMATION_OR_INTELLECTUAL_PROPERTY,
            12: StixIncidentEffect.TERM_REGULATORY_COMPLIANCE_OR_LEGAL_IMPACT,
            13: StixIncidentEffect.TERM_UNINTENDED_ACCESS,
            14: StixIncidentEffect.TERM_USER_DATA_LOSS,
            }


class IntendedEffect(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            1: StixIntendedEffect.TERM_ADVANTAGE,
            2: StixIntendedEffect.TERM_ADVANTAGE_ECONOMIC,
            3: StixIntendedEffect.TERM_ADVANTAGE_MILITARY,
            4: StixIntendedEffect.TERM_ADVANTAGE_POLITICAL,
            5: StixIntendedEffect.TERM_THEFT,
            6: StixIntendedEffect.TERM_THEFT_INTELLECTUAL_PROPERTY,
            7: StixIntendedEffect.TERM_THEFT_CREDENTIAL_THEFT,
            8: StixIntendedEffect.TERM_THEFT_IDENTITY_THEFT,
            9: StixIntendedEffect.TERM_THEFT_THEFT_OF_PROPRIETARY_INFORMATION,
            10: StixIntendedEffect.TERM_ACCOUNT_TAKEOVER,
            11: StixIntendedEffect.TERM_BRAND_DAMAGE,
            12: StixIntendedEffect.TERM_COMPETITIVE_ADVANTAGE,
            13: StixIntendedEffect.TERM_DEGRADATION_OF_SERVICE,
            14: StixIntendedEffect.TERM_DENIAL_AND_DECEPTION,
            15: StixIntendedEffect.TERM_DESTRUCTION,
            16: StixIntendedEffect.TERM_DISRUPTION,
            17: StixIntendedEffect.TERM_EMBARRASSMENT,
            18: StixIntendedEffect.TERM_EXPOSURE,
            19: StixIntendedEffect.TERM_EXTORTION,
            20: StixIntendedEffect.TERM_FRAUD,
            21: StixIntendedEffect.TERM_HARASSMENT,
            22: StixIntendedEffect.TERM_ICS_CONTROL,
            23: StixIntendedEffect.TERM_TRAFFIC_DIVERSION,
            24: StixIntendedEffect.TERM_UNAUTHORIZED_ACCESS
            }


class OwnerShipClass(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            5: StixOwnershipClass.TERM_INTERNALLYOWNED,
            1: StixOwnershipClass.TERM_EMPLOYEEOWNED,
            2: StixOwnershipClass.TERM_PARTNEROWNED,
            3: StixOwnershipClass.TERM_CUSTOMEROWNED,
            4: StixOwnershipClass.TERM_UNKNOWN,
            }


class ManagementClass(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            4: StixManagementClass.TERM_INTERNALLYMANAGED,
            1: StixManagementClass.TERM_EXTERNALLYMANAGEMENT,
            2: StixManagementClass.TERM_COMANAGEMENT,
            3: StixManagementClass.TERM_UNKNOWN,
            }


class LocationClass(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            5: StixLocationClass.TERM_INTERNALLYLOCATED,
            1: StixLocationClass.TERM_EXTERNALLYLOCATED,
            2: StixLocationClass.TERM_COLOCATED,
            3: StixLocationClass.TERM_MOBILE,
            4: StixLocationClass.TERM_UNKNOWN,
            }


class COAStage(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            2: StixCOAStage.TERM_REMEDY,
            1: StixCOAStage.TERM_RESPONSE
            }


class CourseOfActionType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            16: StixCourseOfActionType.TERM_PERIMETER_BLOCKING,
            1: StixCourseOfActionType.TERM_INTERNAL_BLOCKING,
            2: StixCourseOfActionType.TERM_REDIRECTION,
            3: StixCourseOfActionType.TERM_REDIRECTION_HONEY_POT,
            4: StixCourseOfActionType.TERM_HARDENING,
            5: StixCourseOfActionType.TERM_PATCHING,
            6: StixCourseOfActionType.TERM_ERADICATION,
            7: StixCourseOfActionType.TERM_REBUILDING,
            8: StixCourseOfActionType.TERM_TRAINING,
            9: StixCourseOfActionType.TERM_MONITORING,
            10: StixCourseOfActionType.TERM_PHYSICAL_ACCESS_RESTRICTIONS,
            11: StixCourseOfActionType.TERM_LOGICAL_ACCESS_RESTRICTIONS,
            12: StixCourseOfActionType.TERM_PUBLIC_DISCLOSURE,
            13: StixCourseOfActionType.TERM_DIPLOMATIC_ACTIONS,
            14: StixCourseOfActionType.TERM_POLICY_ACTIONS,
            15: StixCourseOfActionType.TERM_OTHER
            }


class CategoriesType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            7: StixIncidentCategory.TERM_EXERCISEORNETWORK_DEFENSE_TESTING,
            1: StixIncidentCategory.TERM_UNAUTHORIZED_ACCESS,
            2: StixIncidentCategory.TERM_DENIAL_OF_SERVICE,
            3: StixIncidentCategory.TERM_MALICIOUS_CODE,
            4: StixIncidentCategory.TERM_IMPROPER_USAGE,
            5: StixIncidentCategory.TERM_SCANSORPROBESORATTEMPTED_ACCESS,
            6: StixIncidentCategory.TERM_INVESTIGATION,
            }


class AssetType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            75: StixAssetType.TERM_BACKUP,
            1: StixAssetType.TERM_DATABASE,
            2: StixAssetType.TERM_DHCP,
            3: StixAssetType.TERM_DIRECTORY,
            4: StixAssetType.TERM_DCS,
            5: StixAssetType.TERM_DNS,
            6: StixAssetType.TERM_FILE,
            7: StixAssetType.TERM_LOG,
            8: StixAssetType.TERM_MAIL,
            9: StixAssetType.TERM_MAINFRAME,
            10: StixAssetType.TERM_PAYMENT_SWITCH,
            11: StixAssetType.TERM_POS_CONTROLLER,
            12: StixAssetType.TERM_PRINT,
            13: StixAssetType.TERM_PROXY,
            14: StixAssetType.TERM_REMOTE_ACCESS,
            15: StixAssetType.TERM_SCADA,
            16: StixAssetType.TERM_WEB_APPLICATION,
            17: StixAssetType.TERM_SERVER,
            18: StixAssetType.TERM_ACCESS_READER,
            19: StixAssetType.TERM_CAMERA,
            20: StixAssetType.TERM_FIREWALL,
            21: StixAssetType.TERM_HSM,
            22: StixAssetType.TERM_IDS,
            23: StixAssetType.TERM_BROADBAND,
            24: StixAssetType.TERM_PBX,
            25: StixAssetType.TERM_PRIVATE_WAN,
            26: StixAssetType.TERM_PLC,
            27: StixAssetType.TERM_PUBLIC_WAN,
            28: StixAssetType.TERM_RTU,
            29: StixAssetType.TERM_ROUTER_OR_SWITCH,
            30: StixAssetType.TERM_SAN,
            31: StixAssetType.TERM_TELEPHONE,
            32: StixAssetType.TERM_VOIP_ADAPTER,
            33: StixAssetType.TERM_LAN,
            34: StixAssetType.TERM_WLAN,
            35: StixAssetType.TERM_NETWORK,
            36: StixAssetType.TERM_AUTH_TOKEN,
            37: StixAssetType.TERM_ATM,
            38: StixAssetType.TERM_DESKTOP,
            39: StixAssetType.TERM_PED_PAD,
            40: StixAssetType.TERM_GAS_TERMINAL,
            41: StixAssetType.TERM_LAPTOP,
            42: StixAssetType.TERM_MEDIA,
            43: StixAssetType.TERM_MOBILE_PHONE,
            44: StixAssetType.TERM_PERIPHERAL,
            45: StixAssetType.TERM_POS_TERMINAL,
            46: StixAssetType.TERM_KIOSK,
            47: StixAssetType.TERM_TABLET,
            48: StixAssetType.TERM_VOIP_PHONE,
            49: StixAssetType.TERM_USER_DEVICE,
            50: StixAssetType.TERM_TAPES,
            51: StixAssetType.TERM_DISK_MEDIA,
            52: StixAssetType.TERM_DOCUMENTS,
            53: StixAssetType.TERM_FLASH_DRIVE,
            54: StixAssetType.TERM_DISK_DRIVE,
            55: StixAssetType.TERM_SMART_CARD,
            56: StixAssetType.TERM_PAYMENT_CARD,
            57: StixAssetType.TERM_ADMINISTRATOR,
            58: StixAssetType.TERM_AUDITOR,
            59: StixAssetType.TERM_CALL_CENTER,
            60: StixAssetType.TERM_CASHIER,
            61: StixAssetType.TERM_CUSTOMER,
            62: StixAssetType.TERM_DEVELOPER,
            63: StixAssetType.TERM_ENDUSER,
            64: StixAssetType.TERM_EXECUTIVE,
            65: StixAssetType.TERM_FINANCE,
            66: StixAssetType.TERM_FORMER_EMPLOYEE,
            67: StixAssetType.TERM_GUARD,
            68: StixAssetType.TERM_HELPDESK,
            69: StixAssetType.TERM_HUMAN_RESOURCES,
            70: StixAssetType.TERM_MAINTENANCE,
            71: StixAssetType.TERM_MANAGER,
            72: StixAssetType.TERM_PARTNER,
            73: StixAssetType.TERM_PERSON,
            74: StixAssetType.TERM_UNKNOWN,
            }


class HighMediumLow(BaseVocab):
  @classmethod
  def get_dictionary(cls):
    return {0: StixHighMediumLow.TERM_NONE,
            5: StixHighMediumLow.TERM_NONE,
            1: StixHighMediumLow.TERM_LOW,
            2: StixHighMediumLow.TERM_MEDIUM,
            3: StixHighMediumLow.TERM_HIGH,
            4: StixHighMediumLow.TERM_UNKNOWN}


class IncidentStatus(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            9: StixIncidentStatus.TERM_NEW,
            1: StixIncidentStatus.TERM_OPEN,
            2: StixIncidentStatus.TERM_STALLED,
            3: StixIncidentStatus.TERM_CONTAINMENT_ACHIEVED,
            4: StixIncidentStatus.TERM_RESTORATION_ACHIEVED,
            5: StixIncidentStatus.TERM_INCIDENT_REPORTED,
            6: StixIncidentStatus.TERM_CLOSED,
            7: StixIncidentStatus.TERM_REJECTED,
            8: StixIncidentStatus.TERM_DELETED,
            }


class LossProperty(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            5: StixLossProperty.TERM_CONFIDENTIALITY,
            1: StixLossProperty.TERM_INTEGRITY,
            2: StixLossProperty.TERM_AVAILABILITY,
            3: StixLossProperty.TERM_ACCOUNTABILITY,
            4: StixLossProperty.TERM_NONREPUDIATION,
            }


class AvailabilityLossType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            7: StixAvailabilityLossType.TERM_DESTRUCTION,
            1: StixAvailabilityLossType.TERM_LOSS,
            2: StixAvailabilityLossType.TERM_INTERRUPTION,
            3: StixAvailabilityLossType.TERM_DEGRADATION,
            4: StixAvailabilityLossType.TERM_ACCELERATION,
            5: StixAvailabilityLossType.TERM_OBSCURATION,
            6: StixAvailabilityLossType.TERM_UNKNOWN,
            }


class LossDuration(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            7: StixLossDuration.TERM_PERMANENT,
            1: StixLossDuration.TERM_WEEKS,
            2: StixLossDuration.TERM_DAYS,
            3: StixLossDuration.TERM_HOURS,
            4: StixLossDuration.TERM_MINUTES,
            5: StixLossDuration.TERM_SECONDS,
            6: StixLossDuration.TERM_UNKNOWN,
            }


class DiscoveryMethod(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            17: StixDiscoveryMethod.TERM_AGENT_DISCLOSURE,
            1: StixDiscoveryMethod.TERM_FRAUD_DETECTION,
            2: StixDiscoveryMethod.TERM_MONITORING_SERVICE,
            3: StixDiscoveryMethod.TERM_LAW_ENFORCEMENT,
            4: StixDiscoveryMethod.TERM_CUSTOMER,
            5: StixDiscoveryMethod.TERM_UNRELATED_PARTY,
            6: StixDiscoveryMethod.TERM_AUDIT,
            7: StixDiscoveryMethod.TERM_ANTIVIRUS,
            8: StixDiscoveryMethod.TERM_INCIDENT_RESPONSE,
            9: StixDiscoveryMethod.TERM_FINANCIAL_AUDIT,
            10: StixDiscoveryMethod.TERM_HIPS,
            11: StixDiscoveryMethod.TERM_IT_AUDIT,
            12: StixDiscoveryMethod.TERM_LOG_REVIEW,
            13: StixDiscoveryMethod.TERM_NIDS,
            14: StixDiscoveryMethod.TERM_SECURITY_ALARM,
            15: StixDiscoveryMethod.TERM_USER,
            16: StixDiscoveryMethod.TERM_UNKNOWN,
            }


class SecurityCompromise(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            4: StixSecurityCompromise.TERM_YES,
            1: StixSecurityCompromise.TERM_SUSPECTED,
            2: StixSecurityCompromise.TERM_NO,
            3: StixSecurityCompromise.TERM_UNKNOWN
            }


class IncidentCategory(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            7: StixIncidentCategory.TERM_EXERCISEORNETWORK_DEFENSE_TESTING,
            1: StixIncidentCategory.TERM_UNAUTHORIZED_ACCESS,
            2: StixIncidentCategory.TERM_DENIAL_OF_SERVICE,
            3: StixIncidentCategory.TERM_MALICIOUS_CODE,
            4: StixIncidentCategory.TERM_IMPROPER_USAGE,
            5: StixIncidentCategory.TERM_SCANSORPROBESORATTEMPTED_ACCESS,
            6: StixIncidentCategory.TERM_INVESTIGATION
            }


class ImpactQualification(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            6: StixImpactQualification.TERM_INSIGNIFICANT,
            1: StixImpactQualification.TERM_DISTRACTING,
            2: StixImpactQualification.TERM_PAINFUL,
            3: StixImpactQualification.TERM_DAMAGING,
            4: StixImpactQualification.TERM_CATASTROPHIC,
            5: StixImpactQualification.TERM_UNKNOWN
            }


class AvailabilityLoss(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            7: StixAvailabilityLossType.TERM_DESTRUCTION,
            1: StixAvailabilityLossType.TERM_LOSS,
            2: StixAvailabilityLossType.TERM_INTERRUPTION,
            3: StixAvailabilityLossType.TERM_DEGRADATION,
            4: StixAvailabilityLossType.TERM_ACCELERATION,
            5: StixAvailabilityLossType.TERM_OBSCURATION,
            6: StixAvailabilityLossType.TERM_UNKNOWN
            }


class IndicatorType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {14: StixIndicatorType.TERM_MALICIOUS_EMAIL,
            1: StixIndicatorType.TERM_IP_WATCHLIST,
            2: StixIndicatorType.TERM_FILE_HASH_WATCHLIST,
            3: StixIndicatorType.TERM_DOMAIN_WATCHLIST,
            4: StixIndicatorType.TERM_URL_WATCHLIST,
            5: StixIndicatorType.TERM_MALWARE_ARTIFACTS,
            6: StixIndicatorType.TERM_C2,
            7: StixIndicatorType.TERM_ANONYMIZATION,
            8: StixIndicatorType.TERM_EXFILTRATION,
            9: StixIndicatorType.TERM_HOST_CHARACTERISTICS,
            10: StixIndicatorType.TERM_COMPROMISED_PKI_CERTIFICATE,
            11: StixIndicatorType.TERM_LOGIN_NAME,
            12: StixIndicatorType.TERM_IMEI_WATCHLIST,
            13: StixIndicatorType.TERM_IMSI_WATCHLIST
            }


class ThreatActorType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            17: StixThreatActorType.TERM_CYBER_ESPIONAGE_OPERATIONS,
            1: StixThreatActorType.TERM_HACKER,
            2: StixThreatActorType.TERM_HACKER_WHITE_HAT,
            3: StixThreatActorType.TERM_HACKER_GRAY_HAT,
            4: StixThreatActorType.TERM_HACKER_BLACK_HAT,
            5: StixThreatActorType.TERM_HACKTIVIST,
            6: StixThreatActorType.TERM_STATE_ACTOR_OR_AGENCY,
            7: StixThreatActorType.TERM_ECRIME_ACTOR_CREDENTIAL_THEFT_BOTNET_OPERATOR,
            8: StixThreatActorType.TERM_ECRIME_ACTOR_CREDENTIAL_THEFT_BOTNET_SERVICE,
            9: StixThreatActorType.TERM_ECRIME_ACTOR_MALWARE_DEVELOPER,
            10: StixThreatActorType.TERM_ECRIME_ACTOR_MONEY_LAUNDERING_NETWORK,
            11: StixThreatActorType.TERM_ECRIME_ACTOR_ORGANIZED_CRIME_ACTOR,
            12: StixThreatActorType.TERM_ECRIME_ACTOR_SPAM_SERVICE,
            13: StixThreatActorType.TERM_ECRIME_ACTOR_TRAFFIC_SERVICE,
            14: StixThreatActorType.TERM_ECRIME_ACTOR_UNDERGROUND_CALL_SERVICE,
            15: StixThreatActorType.TERM_INSIDER_THREAT,
            16: StixThreatActorType.TERM_DISGRUNTLED_CUSTOMER_OR_USER,
            }


class Motivation(BaseVocab):
  
  @classmethod
  def get_dictionary(cls):
    return {
            14: StixMotivation.TERM_IDEOLOGICAL,
            1: StixMotivation.TERM_IDEOLOGICAL_ANTICORRUPTION,
            2: StixMotivation.TERM_IDEOLOGICAL_ANTIESTABLISHMENT,
            3: StixMotivation.TERM_IDEOLOGICAL_ENVIRONMENTAL,
            4: StixMotivation.TERM_IDEOLOGICAL_ETHNIC_OR_NATIONALIST,
            5: StixMotivation.TERM_IDEOLOGICAL_INFORMATION_FREEDOM,
            6: StixMotivation.TERM_IDEOLOGICAL_RELIGIOUS,
            7: StixMotivation.TERM_IDEOLOGICAL_SECURITY_AWARENESS,
            8: StixMotivation.TERM_IDEOLOGICAL_HUMAN_RIGHTS,
            9: StixMotivation.TERM_EGO,
            10: StixMotivation.TERM_FINANCIAL_OR_ECONOMIC,
            11: StixMotivation.TERM_MILITARY,
            12: StixMotivation.TERM_OPPORTUNISTIC,
            13: StixMotivation.TERM_POLITICAL,
            }


class ThreatActorSophistication(BaseVocab):
  
  @classmethod
  def get_dictionary(cls):
    return {
            5: StixThreatActorSophistication.TERM_INNOVATOR,
            1: StixThreatActorSophistication.TERM_EXPERT,
            2: StixThreatActorSophistication.TERM_PRACTITIONER,
            3: StixThreatActorSophistication.TERM_NOVICE,
            4: StixThreatActorSophistication.TERM_ASPIRANT,
            }


class PlanningAndOperationalSupport(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            22: StixPlanningAndOperationalSupport.TERM_DATA_EXPLOITATION,
            1: StixPlanningAndOperationalSupport.TERM_DATA_EXPLOITATION_ANALYTIC_SUPPORT,
            2: StixPlanningAndOperationalSupport.TERM_DATA_EXPLOITATION_TRANSLATION_SUPPORT,
            3: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES,
            4: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_ACADEMIC,
            5: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_COMMERCIAL,
            6: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_GOVERNMENT,
            7: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_HACKTIVIST_OR_GRASSROOT,
            8: StixPlanningAndOperationalSupport.TERM_FINANCIAL_RESOURCES_NONATTRIBUTABLE_FINANCE,
            9: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT,
            10: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_CONTRACTING_AND_HIRING,
            11: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_DOCUMENT_EXPLOITATION_DOCEX_TRAINING,
            12: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_INTERNAL_TRAINING,
            13: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_MILITARY_PROGRAMS,
            14: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_SECURITY_OR_HACKER_CONFERENCES,
            15: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_UNDERGROUND_FORUMS,
            16: StixPlanningAndOperationalSupport.TERM_SKILL_DEVELOPMENT_OR_RECRUITMENT_UNIVERSITY_PROGRAMS,
            17: StixPlanningAndOperationalSupport.TERM_PLANNING,
            18: StixPlanningAndOperationalSupport.TERM_PLANNING_OPERATIONAL_COVER_PLAN,
            19: StixPlanningAndOperationalSupport.TERM_PLANNING_OPENSOURCE_INTELLIGENCE_OSINT_GATHERING,
            20: StixPlanningAndOperationalSupport.TERM_PLANNING_PREOPERATIONAL_SURVEILLANCE_AND_RECONNAISSANCE,
            21: StixPlanningAndOperationalSupport.TERM_PLANNING_TARGET_SELECTION,
            }

class MalwareType(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            18: StixMalwareType.TERM_AUTOMATED_TRANSFER_SCRIPTS,
            1: StixMalwareType.TERM_ADWARE,
            2: StixMalwareType.TERM_DIALER,
            3: StixMalwareType.TERM_BOT,
            4: StixMalwareType.TERM_BOT_CREDENTIAL_THEFT,
            5: StixMalwareType.TERM_BOT_DDOS,
            6: StixMalwareType.TERM_BOT_LOADER ,
            7: StixMalwareType.TERM_BOT_SPAM,
            8: StixMalwareType.TERM_DOS_OR_DDOS,
            9: StixMalwareType.TERM_DOS_OR_DDOS_PARTICIPATORY,
            10: StixMalwareType.TERM_DOS_OR_DDOS_SCRIPT,
            11: StixMalwareType.TERM_DOS_OR_DDOS_STRESS_TEST_TOOLS ,
            12: StixMalwareType.TERM_EXPLOIT_KITS,
            13: StixMalwareType.TERM_POS_OR_ATM_MALWARE ,
            14: StixMalwareType.TERM_RANSOMWARE ,
            15: StixMalwareType.TERM_REMOTE_ACCESS_TROJAN ,
            16: StixMalwareType.TERM_ROGUE_ANTIVIRUS ,
            17: StixMalwareType.TERM_ROOTKIT
            }


class TargetedInformation(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            9: StixInformationType.TERM_INFORMATION_ASSETS,
            1: StixInformationType.TERM_INFORMATION_ASSETS_CORPORATE_EMPLOYEE_INFORMATION,
            2: StixInformationType.TERM_INFORMATION_ASSETS_CUSTOMER_PII,
            3: StixInformationType.TERM_INFORMATION_ASSETS_EMAIL_LISTS_OR_ARCHIVES,
            4: StixInformationType.TERM_INFORMATION_ASSETS_FINANCIAL_DATA,
            5: StixInformationType.TERM_INFORMATION_ASSETS_INTELLECTUAL_PROPERTY,
            6: StixInformationType.TERM_INFORMATION_ASSETS_MOBILE_PHONE_CONTACTS,
            7: StixInformationType.TERM_INFORMATION_ASSETS_USER_CREDENTIALS,
            8: StixInformationType.TERM_AUTHENTICATION_COOKIES,
            }

class TargetedSystems(BaseVocab):

  @classmethod
  def get_dictionary(cls):
    return {
            27: StixSystemType.TERM_ENTERPRISE_SYSTEMS,
            1: StixSystemType.TERM_ENTERPRISE_SYSTEMS_APPLICATION_LAYER,
            2: StixSystemType.TERM_ENTERPRISE_SYSTEMS_DATABASE_LAYER,
            3: StixSystemType.TERM_ENTERPRISE_SYSTEMS_ENTERPRISE_TECHNOLOGIES_AND_SUPPORT_INFRASTRUCTURE,
            4: StixSystemType.TERM_ENTERPRISE_SYSTEMS_NETWORK_SYSTEMS,
            5: StixSystemType.TERM_ENTERPRISE_SYSTEMS_NETWORKING_DEVICES,
            6: StixSystemType.TERM_ENTERPRISE_SYSTEMS_WEB_LAYER,
            7: StixSystemType.TERM_ENTERPRISE_SYSTEMS_VOIP,
            8: StixSystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS,
            9: StixSystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_EQUIPMENT_UNDER_CONTROL,
            10: StixSystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_OPERATIONS_MANAGEMENT,
            11: StixSystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_SAFETY_PROTECTION_AND_LOCAL_CONTROL,
            12: StixSystemType.TERM_INDUSTRIAL_CONTROL_SYSTEMS_SUPERVISORY_CONTROL,
            13: StixSystemType.TERM_MOBILE_SYSTEMS,
            14: StixSystemType.TERM_MOBILE_SYSTEMS_MOBILE_OPERATING_SYSTEMS,
            15: StixSystemType.TERM_MOBILE_SYSTEMS_NEAR_FIELD_COMMUNICATIONS,
            16: StixSystemType.TERM_MOBILE_SYSTEMS_MOBILE_DEVICES,
            17: StixSystemType.TERM_THIRDPARTY_SERVICES,
            18: StixSystemType.TERM_THIRDPARTY_SERVICES_APPLICATION_STORES,
            19: StixSystemType.TERM_THIRDPARTY_SERVICES_CLOUD_SERVICES,
            20: StixSystemType.TERM_THIRDPARTY_SERVICES_SECURITY_VENDORS,
            21: StixSystemType.TERM_THIRDPARTY_SERVICES_SOCIAL_MEDIA,
            22: StixSystemType.TERM_THIRDPARTY_SERVICES_SOFTWARE_UPDATE,
            23: StixSystemType.TERM_USERS,
            24: StixSystemType.TERM_USERS_APPLICATION_AND_SOFTWARE,
            25: StixSystemType.TERM_USERS_WORKSTATION,
            26: StixSystemType.TERM_USERS_REMOVABLE_MEDIA,
            }


class PackageIntent(BaseVocab):
  
  @classmethod
  def get_dictionary(cls):
    return {
            20: StixPackageIntent.TERM_COLLECTIVE_THREAT_INTELLIGENCE,
            1: StixPackageIntent.TERM_THREAT_REPORT,
            2: StixPackageIntent.TERM_INDICATORS,
            3: StixPackageIntent.TERM_INDICATORS_PHISHING ,
            4: StixPackageIntent.TERM_INDICATORS_WATCHLIST ,
            5: StixPackageIntent.TERM_INDICATORS_MALWARE_ARTIFACTS ,
            6: StixPackageIntent.TERM_INDICATORS_NETWORK_ACTIVITY,
            7: StixPackageIntent.TERM_INDICATORS_ENDPOINT_CHARACTERISTICS,
            8: StixPackageIntent.TERM_CAMPAIGN_CHARACTERIZATION,
            9: StixPackageIntent.TERM_THREAT_ACTOR_CHARACTERIZATION ,
            10: StixPackageIntent.TERM_EXPLOIT_CHARACTERIZATION ,
            11: StixPackageIntent.TERM_ATTACK_PATTERN_CHARACTERIZATION,
            12: StixPackageIntent.TERM_MALWARE_CHARACTERIZATION,
            13: StixPackageIntent.TERM_TTP_INFRASTRUCTURE,
            14: StixPackageIntent.TERM_TTP_TOOLS,
            15: StixPackageIntent.TERM_COURSES_OF_ACTION,
            16: StixPackageIntent.TERM_INCIDENT,
            17: StixPackageIntent.TERM_OBSERVATIONS,
            18: StixPackageIntent.TERM_OBSERVATIONS_EMAIL,
            19: StixPackageIntent.TERM_MALWARE_SAMPLES
            }


class InformationSourceRole(BaseVocab):

  @staticmethod
  def get_dictionary():
    return {
            4: StixInformationSourceRole.TERM_INITIAL_AUTHOR,
            1: StixInformationSourceRole.TERM_CONTENT_ENHANCERORREFINER,
            2: StixInformationSourceRole.TERM_AGGREGATOR,
            3: StixInformationSourceRole.TERM_TRANSFORMERORTRANSLATOR,
            }
