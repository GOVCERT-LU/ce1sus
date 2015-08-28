# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 27, 2015
"""


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

DISTRIBUTION_TO_TLP_MAP = {'0': 'Red',
                           '1': 'Amber',
                           '2': 'Amber',
                           '3': 'Green'
                           }
#Taken out of MISP2STIX
#TLP-mapping = {'0' : 'AMBER', '1' : 'GREEN', '2' : 'GREEN', '3' : 'GREEN'} 

RISK_MAP = {'1': 'High',
            '2': 'Medium',
            '3': 'Low',
            '4': 'None',
            }

ANALYSIS_MAP = {'0': 'Opened',
                '1': 'Opened',
                '2': 'Completed',
                }

MISP_MAP = {            
            'Internal reference/link': 'ce1sus-Report-Reference-link',
            'Internal reference/comment': 'ce1sus-Report-Reference-comment',
            'Internal reference/text': 'ce1sus-Report-Reference-comment',
            'Internal reference/other': 'ce1sus-Report-Reference-comment',

            #PartyName(person-names = [attribute["value"]])
            'Targeting data/target-user': 'stix-CIQIdentity3_0Instance-STIXCIQIdentity3_0-PartyName',
            'Targeting data/target-email': 'stix-CIQIdentity3_0Instance-STIXCIQIdentity3_0-ElectronicAddressIdentifier',
            'Targeting data/target-machine': 'stix-AffectedAsset',
            #PartyName(organisation-names = [attribute["value"]])
            'Targeting data/target-org': 'stix-CIQIdentity3_0Instance-STIXCIQIdentity3_0-PartyName',
            'Targeting data/target-location': 'stix-CIQIdentity3_0Instance-STIXCIQIdentity3_0-Address-FreeTextAddress',
            #value = ["External target: " + attribute["value"]
            'Targeting data/target-external': 'stix-CIQIdentity3_0Instance-STIXCIQIdentity3_0-PartyName',
            'Targeting data/target-comment': 'ce1sus-Report-Reference-comment',

            'Antivirus detection/link': 'ce1sus-Report-Reference-link',
            'Antivirus detection/comment': 'ce1sus-Report-Reference-comment',
            'Antivirus detection/text': 'ce1sus-Report-Reference-comment',
            'Antivirus detection/attachment': 'cybox-Observable-File-Raw_Artifact',
            'Antivirus detection/other': 'ce1sus-Report-Reference-comment',

            'Payload delivery/md5':'cybox-Observable-File-hash_md5',
            'Payload delivery/sha1':'cybox-Observable-File-hash_sha1',
            'Payload delivery/sha256':'cybox-Observable-File-hash_sha256',
            'Payload delivery/filename':'cybox-Observable-File-File_Name',
            'Payload delivery/filename|md5':'cybox-Observable-File-hash_md5',
            'Payload delivery/filename|sha1':'cybox-Observable-File-hash_sha1',
            'Payload delivery/filename|sha256':'cybox-Observable-File-hash_sha256',
            'Payload delivery/ip-src':'cybox-Observable-Address',
            'Payload delivery/ip-dst':'cybox-Observable-Address',
            'Payload delivery/hostname':'cybox-Observable-Hostname-Hostname_Value',
            'Payload delivery/email-src':'cybox-Observable-EmailMessage-email_from',
            'Payload delivery/email-dst':'cybox-Observable-EmailMessage-email_to',
            'Payload delivery/email-subject':'cybox-Observable-EmailMessage-email_subject',
            'Payload delivery/email-attachment':'cybox-Observable-EmailMessage-email_attachment_file_name',
            'Payload delivery/url':'cybox-Observable-URI-url',
            #'Payload delivery/user-agent':'cybox-Observable-HTTPSession-HTTPRequestResponse-HTTPClientRequest-HTTPRequestHeaderFields',
            'Payload delivery/user-agent':'cybox-Observable-HTTPSession-User_Agent',
            'Payload delivery/AS':'cybox-Observable-AutonomousSystem',
            'Payload delivery/pattern-in-file':'ce1sus-Observable-File-pattern_in_file',
            'Payload delivery/pattern-in-traffic':'',
            'Payload delivery/yara':'stix-Indicator-YaraTestMechanism',
            'Payload delivery/attachment':'cybox-Observable-File-Raw_Artifact',
            'Payload delivery/malware-sample':'cybox-Observable-File-Raw_Artifact',
            'Payload delivery/link':'cybox-Observable-URI-url',
            'Payload delivery/comment':'',
            'Payload delivery/text':'',
            'Payload delivery/vulnerability':'stix-TTP-Vulnerability',
            'Payload delivery/other':'',

            'Artifacts dropped/md5':'cybox-Observable-File-hash_md5',
            'Artifacts dropped/sha1':'cybox-Observable-File-hash_sha1',
            'Artifacts dropped/sha256':'cybox-Observable-File-hash_sha256',
            'Artifacts dropped/filename':'cybox-Observable-File-File_Name',
            'Artifacts dropped/filename|md5':'cybox-Observable-File-hash_md5',
            'Artifacts dropped/filename|sha1':'cybox-Observable-File-hash_sha1',
            'Artifacts dropped/filename|sha256':'cybox-Observable-File-hash_sha256',
            'Artifacts dropped/regkey':'cybox-Observable-WinRegistryKey',
            'Artifacts dropped/regkey|value':'cybox-Observable-WinRegistryKey-RegistryValue',
            'Artifacts dropped/pattern-in-file':'ce1sus-Observable-File-pattern_in_file',
            'Artifacts dropped/pattern-in-memory':'ce1sus-Observable-Memory-pattern_in_memory',
            'Artifacts dropped/yara':'stix-Indicator-YaraTestMechanism',
            'Artifacts dropped/attachment':'cybox-Observable-File-Raw_Artifact',
            'Artifacts dropped/malware-sample':'cybox-Observable-File-Raw_Artifact',
            'Artifacts dropped/comment':'',
            'Artifacts dropped/text':'',
            'Artifacts dropped/other':'',
            'Artifacts dropped/named pipe':'cybox-Observable-Pipe-Pipe_Name',
            'Artifacts dropped/mutex':'cybox-Observable-Mutex-Mutex_name',

            'Payload installation/md5':'cybox-Observable-File-hash_md5',
            'Payload installation/sha1':'cybox-Observable-File-hash_sha1',
            'Payload installation/sha256':'cybox-Observable-File-hash_sha256',
            'Payload installation/filename':'cybox-Observable-File-File_Name',
            'Payload installation/filename|md5':'cybox-Observable-File-hash_md5',
            'Payload installation/filename|sha1':'cybox-Observable-File-hash_sha1',
            'Payload installation/filename|sha256':'cybox-Observable-File-hash_sha256',
            'Payload installation/pattern-in-file':'ce1sus-Observable-File-pattern_in_file',
            'Payload installation/pattern-in-traffic':'',
            'Payload installation/pattern-in-memory':'ce1sus-Observable-Memory-pattern_in_memory',
            'Payload installation/yara':'stix-Indicator-YaraTestMechanism',
            'Payload installation/vulnerability':'stix-TTP-Vulnerability',
            'Payload installation/attachment':'cybox-Observable-File-Raw_Artifact',
            'Payload installation/malware-sample':'cybox-Observable-File-Raw_Artifact',
            'Payload installation/comment':'',
            'Payload installation/text':'',
            'Payload installation/other':'',


            'Persistence mechanism/filename':'cybox-Observable-File-File_Name',
            'Persistence mechanism/regkey':'cybox-Observable-WinRegistryKey',
            'Persistence mechanism/regkey|value':'cybox-Observable-WinRegistryKey-RegistryValue',
            'Persistence mechanism/comment':'',
            'Persistence mechanism/text':'',
            'Persistence mechanism/other':'',


            'Network activity/ip-src':'cybox-Observable-Address',
            'Network activity/ip-dst':'cybox-Observable-Address',
            'Network activity/hostname':'cybox-Observable-Hostname-Hostname_Value',
            'Network activity/domain':'cybox-Observable-Domain-DomainName_Value',
            'Network activity/email-dst':'cybox-Observable-EmailMessage-email_to',
            'Network activity/url':'cybox-Observable-URI-url',
            'Network activity/user-agent':'cybox-Observable-HTTPSession-User_Agent',
            'Network activity/http-method':'cybox-Observable-HTTPSession-HTTPRequestResponse-HTTPClientRequest-HTTPRequestLine',
            'Network activity/AS':'cybox-Observable-AutonomousSystem',
            'Network activity/snort':'stix-Indicator-SnortTestMechanism',
            'Network activity/pattern-in-file':'ce1sus-Observable-File-pattern_in_file',
            'Network activity/pattern-in-traffic':'',
            'Network activity/attachment':'cybox-Observable-File-Raw_Artifact',
            'Network activity/text':'',
            'Network activity/other':'',


            'Payload type/comment':'stix-TTP-Behaviour-MalwareInstance',
            'Payload type/text':'stix-TTP-Behaviour-MalwareInstance',
            'Payload type/other':'stix-TTP-Behaviour-MalwareInstance',

            'Attribution/comment':'stix-ThreatActor',
            'Attribution/text':'stix-ThreatActor',
            'Attribution/other':'stix-ThreatActor',

            'External analysis/md5':'cybox-Observable-File-hash_md5',
            'External analysis/sha1':'cybox-Observable-File-hash_sha1',
            'External analysis/sha256':'cybox-Observable-File-hash_sha256',
            'External analysis/filename':'cybox-Observable-File',
            'External analysis/filename|md5':'cybox-Observable-File-hash_md5',
            'External analysis/filename|sha1':'cybox-Observable-File-hash_sha1',
            'External analysis/filename|sha256':'cybox-Observable-File-hash_sha256',
            'External analysis/ip-src':'cybox-Observable-Address',
            'External analysis/ip-dst':'cybox-Observable-Address',
            'External analysis/hostname':'cybox-Observable-Hostname-Hostname_Value',
            'External analysis/domain':'cybox-Observable-Domain-DomainName_Value',
            #ATTENTION: CAN BE AN URL TO A REFERENCE SITE i.e. virustotal
            'External analysis/url':'cybox-Observable-URI-url',
            'External analysis/user-agent':'cybox-Observable-HTTPSession-User_Agent',
            'External analysis/regkey':'cybox-Observable-WinRegistryKey',
            'External analysis/regkey|value':'cybox-Observable-WinRegistryKey-RegistryValue',
            'External analysis/AS':'cybox-Observable-AutonomousSystem',
            'External analysis/snort':'stix-Indicator-SnortTestMechanism',
            'External analysis/pattern-in-file':'ce1sus-Observable-File-pattern_in_file',
            'External analysis/pattern-in-traffic':'',
            'External analysis/pattern-in-memory':'ce1sus-Observable-Memory-pattern_in_memory',
            'External analysis/vulnerability':'stix-TTP-Vulnerability',
            'External analysis/attachment':'cybox-Observable-File-Raw_Artifact',
            'External analysis/malware-sample':'cybox-Observable-Artifact',
            'External analysis/link':'ce1sus-Report-Reference-link',
            'External analysis/comment':'',
            'External analysis/text':'',
            'External analysis/other':'',

            'Other/comment':'',
            'Other/text':'',
            'Other/other':'',
            }

def get_tlp(distribution):
  return DISTRIBUTION_TO_TLP_MAP.get(distribution, 'Amber')

def get_container_object_attribute(category, type_):
  mapping = MISP_MAP.get('{0}/{1}'.format(category, type_), None)
  if mapping:
    splitted = mapping.split('-')
    if len(splitted) > 3:
      container = splitted[1]
      object_ = splitted[2]
      attribute = splitted[3]
      return container, object_, attribute
    elif len(splitted) > 2:
      container = splitted[1]
      object_ = splitted[2]
      return container, object_, None
    elif mapping == 'MANUAL':
      return mapping, None, None

  return None, None, None


