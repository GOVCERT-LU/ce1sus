# -*- coding: utf-8 -*-

"""
(Description)

Created on 3 Sep 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from ce1sus.common.utils import table_code
from ce1sus.db.classes.internal.common import Properties
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType, UnicodeTextType
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_MALWARETYPE_PATH = Table('rel_malwaretype_path', getattr(Base, 'metadata'),
                                    Column('malwaretype_id', BigIntegerType, ForeignKey('malwaretypes.malwaretype_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_OBJECT_PATH = Table('rel_object_path', getattr(Base, 'metadata'),
                                    Column('object_id', BigIntegerType, ForeignKey('objects.object_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_ACTIVITY_PATH = Table('rel_activity_path', getattr(Base, 'metadata'),
                                    Column('activity_id', BigIntegerType, ForeignKey('activitys.activity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INDICATOR_PATH = Table('rel_indicator_path', getattr(Base, 'metadata'),
                                    Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_LEVERAGEDTTP_PATH = Table('rel_leveragedttp_path', getattr(Base, 'metadata'),
                                    Column('leveragedttp_id', BigIntegerType, ForeignKey('leveragedttps.leveragedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_COATIME_PATH = Table('rel_coatime_path', getattr(Base, 'metadata'),
                                    Column('coatime_id', BigIntegerType, ForeignKey('coatimes.coatime_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_IMPACTASSESSMENT_PATH = Table('rel_impactassessment_path', getattr(Base, 'metadata'),
                                    Column('impactassessment_id', BigIntegerType, ForeignKey('impactassessments.impactassessment_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_CAMPAIGN_PATH = Table('rel_campaign_path', getattr(Base, 'metadata'),
                                    Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDOBSERVABLE_PATH = Table('rel_relatedobservable_path', getattr(Base, 'metadata'),
                                    Column('relatedobservable_id', BigIntegerType, ForeignKey('relatedobservables.relatedobservable_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_VULNREFERENCE_PATH = Table('rel_vulnreference_path', getattr(Base, 'metadata'),
                                    Column('vulnreference_id', BigIntegerType, ForeignKey('vulnreferences.vulnreference_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDIDENTITY_PATH = Table('rel_relatedidentity_path', getattr(Base, 'metadata'),
                                    Column('relatedidentity_id', BigIntegerType, ForeignKey('relatedidentitys.relatedidentity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_MARKINGSTUCTURE_PATH = Table('rel_markingstructure_path', getattr(Base, 'metadata'),
                                    Column('markingstructure_id', BigIntegerType, ForeignKey('markingstructures.markingstructure_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDEXPLOITTARGET_PATH = Table('rel_relatedexploittarget_path', getattr(Base, 'metadata'),
                                    Column('relatedexploittarget_id', BigIntegerType, ForeignKey('relatedexploittargets.relatedexploittarget_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_OBJECTIVE_PATH = Table('rel_objective_path', getattr(Base, 'metadata'),
                                    Column('objective_id', BigIntegerType, ForeignKey('objectives.objective_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_CONFIDENCE_PATH = Table('rel_confidence_path', getattr(Base, 'metadata'),
                                    Column('confidence_id', BigIntegerType, ForeignKey('confidences.confidence_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_TARGETEDSYSTEM_PATH = Table('rel_targetedsystems_path', getattr(Base, 'metadata'),
                                    Column('targetedsystems_id', BigIntegerType, ForeignKey('targetedsystemss.targetedsystems_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INCIDENT_PATH = Table('rel_incident_path', getattr(Base, 'metadata'),
                                    Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_OBSERVABLEKEYWORD_PATH = Table('rel_observablekeyword_path', getattr(Base, 'metadata'),
                                    Column('observablekeyword_id', BigIntegerType, ForeignKey('observablekeywords.observablekeyword_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_MALWAREINSTANCE_PATH = Table('rel_malwareinstance_path', getattr(Base, 'metadata'),
                                    Column('malwareinstance_id', BigIntegerType, ForeignKey('malwareinstances.malwareinstance_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDOBJECT_PATH = Table('rel_relatedobject_path', getattr(Base, 'metadata'),
                                    Column('relatedobject_id', BigIntegerType, ForeignKey('relatedobjects.relatedobject_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_PROPERTYAFFECTED_PATH = Table('rel_propertyaffected_path', getattr(Base, 'metadata'),
                                    Column('propertyaffected_id', BigIntegerType, ForeignKey('propertyaffecteds.propertyaffected_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_THREATACTORTYPE_PATH = Table('rel_threatactortype_path', getattr(Base, 'metadata'),
                                    Column('threatactortype_id', BigIntegerType, ForeignKey('threatactortypes.threatactortype_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_ASSETTYPE_PATH = Table('rel_assettype_path', getattr(Base, 'metadata'),
                                    Column('assettype_id', BigIntegerType, ForeignKey('assettypes.assettype_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_CONFIGURATION_PATH = Table('rel_configuration_path', getattr(Base, 'metadata'),
                                    Column('configuration_id', BigIntegerType, ForeignKey('configurations.configuration_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_NAME_PATH = Table('rel_name_path', getattr(Base, 'metadata'),
                                    Column('name_id', BigIntegerType, ForeignKey('names.name_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_COA_PATH = Table('rel_courseofaction_path', getattr(Base, 'metadata'),
                                    Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INFRASTRUCTURE_PATH = Table('rel_infrastructure_path', getattr(Base, 'metadata'),
                                    Column('infrastructure_id', BigIntegerType, ForeignKey('infrastructures.infrastructure_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_STRUCTUREDTEXT_PATH = Table('rel_structuredtext_path', getattr(Base, 'metadata'),
                                    Column('structuredtext_id', BigIntegerType, ForeignKey('structuredtexts.structuredtext_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_TOOLINFORMATION_PATH = Table('rel_toolinformation_path', getattr(Base, 'metadata'),
                                    Column('toolinformation_id', BigIntegerType, ForeignKey('toolinformations.toolinformation_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDTHREATACTOR_PATH = Table('rel_relatedthreatactor_path', getattr(Base, 'metadata'),
                                    Column('relatedthreatactor_id', BigIntegerType, ForeignKey('relatedthreatactors.relatedthreatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDPACKAGEREF_PATH = Table('rel_relatedpackageref_path', getattr(Base, 'metadata'),
                                    Column('relatedpackageref_id', BigIntegerType, ForeignKey('relatedpackagerefs.relatedpackageref_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_STIXHEADER_PATH = Table('rel_stixheader_path', getattr(Base, 'metadata'),
                                    Column('stixheader_id', BigIntegerType, ForeignKey('stixheaders.stixheader_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_REPORT_PATH = Table('rel_report_path', getattr(Base, 'metadata'),
                                    Column('report_id', BigIntegerType, ForeignKey('reports.report_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_ATTRIBUTE_PATH = Table('rel_attribute_path', getattr(Base, 'metadata'),
                                    Column('attribute_id', BigIntegerType, ForeignKey('attributes.attribute_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_TTP_PATH = Table('rel_ttp_path', getattr(Base, 'metadata'),
                                    Column('ttp_id', BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_OBSERVABLE_PATH = Table('rel_observable_path', getattr(Base, 'metadata'),
                                    Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EVENT_PATH = Table('rel_event_path', getattr(Base, 'metadata'),
                                    Column('event_id', BigIntegerType, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_REFERENCE_PATH = Table('rel_reference_path', getattr(Base, 'metadata'),
                                    Column('reference_id', BigIntegerType, ForeignKey('references.reference_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_STATEMENT_PATH = Table('rel_statement_path', getattr(Base, 'metadata'),
                                    Column('statement_id', BigIntegerType, ForeignKey('statements.statement_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_AFFECTEDASSET_PATH = Table('rel_affectedasset_path', getattr(Base, 'metadata'),
                                    Column('affectedasset_id', BigIntegerType, ForeignKey('affectedassets.affectedasset_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_PAOS_PATH = Table('rel_planningandoperationalsupport_path', getattr(Base, 'metadata'),
                                    Column('planningandoperationalsupport_id', BigIntegerType, ForeignKey('planningandoperationalsupports.planningandoperationalsupport_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDINCIDENT_PATH = Table('rel_relatedincident_path', getattr(Base, 'metadata'),
                                    Column('relatedincident_id', BigIntegerType, ForeignKey('relatedincidents.relatedincident_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_SOPHISICATION_PATH = Table('rel_sophistication_path', getattr(Base, 'metadata'),
                                    Column('sophistication_id', BigIntegerType, ForeignKey('sophistications.sophistication_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_DISCOVERYMETHOD_PATH = Table('rel_discoverymethod_path', getattr(Base, 'metadata'),
                                    Column('discoverymethod_id', BigIntegerType, ForeignKey('discoverymethods.discoverymethod_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDPACKAGE_PATH = Table('rel_relatedpackage_path', getattr(Base, 'metadata'),
                                    Column('relatedpackage_id', BigIntegerType, ForeignKey('relatedpackages.relatedpackage_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INFORMATIONSOURCE_PATH = Table('rel_informationsource_path', getattr(Base, 'metadata'),
                                    Column('informationsource_id', BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_IDENTITY_PATH = Table('rel_identity_path', getattr(Base, 'metadata'),
                                    Column('identity_id', BigIntegerType, ForeignKey('identitys.identity_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_OBSERVABLECOMPOSITION_PATH = Table('rel_observablecomposition_path', getattr(Base, 'metadata'),
                                    Column('observablecomposition_id', BigIntegerType, ForeignKey('observablecompositions.observablecomposition_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INCIDENTCATEGORY_PATH = Table('rel_incidentcategory_path', getattr(Base, 'metadata'),
                                    Column('incidentcategory_id', BigIntegerType, ForeignKey('incidentcategorys.incidentcategory_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_VULNERABILITY_PATH = Table('rel_vulnerability_path', getattr(Base, 'metadata'),
                                    Column('vulnerability_id', BigIntegerType, ForeignKey('vulnerabilitys.vulnerability_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_LOSSINFORMATION_PATH = Table('rel_lossestimation_path', getattr(Base, 'metadata'),
                                    Column('lossestimation_id', BigIntegerType, ForeignKey('lossestimations.lossestimation_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EXPLOIT_PATH = Table('rel_exploit_path', getattr(Base, 'metadata'),
                                    Column('exploit_id', BigIntegerType, ForeignKey('exploits.exploit_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_DIS_PATH = Table('rel_directimpactsummary_path', getattr(Base, 'metadata'),
                                    Column('directimpactsummary_id', BigIntegerType, ForeignKey('directimpactsummarys.directimpactsummary_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_CYBOXTIME_PATH = Table('rel_cyboxtime_path', getattr(Base, 'metadata'),
                                    Column('cyboxtime_id', BigIntegerType, ForeignKey('cyboxtimes.cyboxtime_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_TLE_PATH = Table('rel_totallossestimation_path', getattr(Base, 'metadata'),
                                    Column('totallossestimation_id', BigIntegerType, ForeignKey('totallossestimations.totallossestimation_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_BEHAVIOUR_PATH = Table('rel_behavior_path', getattr(Base, 'metadata'),
                                    Column('behavior_id', BigIntegerType, ForeignKey('behaviors.behavior_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RESOURCE_PATH = Table('rel_resource_path', getattr(Base, 'metadata'),
                                    Column('resource_id', BigIntegerType, ForeignKey('resources.resource_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_KILLCHAINPAHSEREFERENCE_PATH = Table('rel_killchainphasereference_path', getattr(Base, 'metadata'),
                                    Column('killchainphasereference_id', BigIntegerType, ForeignKey('killchainphasereferences.killchainphasereference_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_MARKINGSPECIFIACTION_PATH = Table('rel_markingspecification_path', getattr(Base, 'metadata'),
                                    Column('markingspecification_id', BigIntegerType, ForeignKey('markingspecifications.markingspecification_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_WEAKNESS_PATH = Table('rel_weakness_path', getattr(Base, 'metadata'),
                                    Column('weakness_id', BigIntegerType, ForeignKey('weaknesss.weakness_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EXPLOITTAGET_PATH = Table('rel_exploittarget_path', getattr(Base, 'metadata'),
                                    Column('exploittarget_id', BigIntegerType, ForeignKey('exploittargets.exploittarget_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_COATAKEN_PATH = Table('rel_coataken_path', getattr(Base, 'metadata'),
                                    Column('coataken_id', BigIntegerType, ForeignKey('coatakens.coataken_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_COAREQUESTED_PATH = Table('rel_coarequested_path', getattr(Base, 'metadata'),
                                    Column('coarequested_id', BigIntegerType, ForeignKey('coarequesteds.coarequested_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_VALIDTIME_PATH = Table('rel_validtime_path', getattr(Base, 'metadata'),
                                    Column('validtimeposition_id', BigIntegerType, ForeignKey('validtimepositions.validtimeposition_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_TIME_PATH = Table('rel_time_path', getattr(Base, 'metadata'),
                                    Column('time_id', BigIntegerType, ForeignKey('stixtimes.time_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INDENDEDEFFECT_PATH = Table('rel_intendedeffect_path', getattr(Base, 'metadata'),
                                    Column('intendedeffect_id', BigIntegerType, ForeignKey('intendedeffects.intendedeffect_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_MALWARENAME_PATH = Table('rel_malwarename_path', getattr(Base, 'metadata'),
                                    Column('malwarename_id', BigIntegerType, ForeignKey('malwarenames.malwarename_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_BASETESTMECHANISM_PATH = Table('rel_basetestmechanism_path', getattr(Base, 'metadata'),
                                    Column('basetestmechanism_id', BigIntegerType, ForeignKey('basetestmechanisms.basetestmechanism_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_IIS_PATH = Table('rel_indirectimpactsummary_path', getattr(Base, 'metadata'),
                                    Column('indirectimpactsummary_id', BigIntegerType, ForeignKey('indirectimpactsummarys.indirectimpactsummary_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_HISTORYITEM_PATH = Table('rel_historyitem_path', getattr(Base, 'metadata'),
                                    Column('historyitem_id', BigIntegerType, ForeignKey('historyitems.historyitem_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_SIGHTING_PATH = Table('rel_sighting_path', getattr(Base, 'metadata'),
                                    Column('sighting_id', BigIntegerType, ForeignKey('sightings.sighting_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_JOURNALENTRY_PATH = Table('rel_journalentry_path', getattr(Base, 'metadata'),
                                    Column('journalentry_id', BigIntegerType, ForeignKey('journalentrys.journalentry_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_VOCABSTRING_PATH = Table('rel_vocabstring_path', getattr(Base, 'metadata'),
                                    Column('vocabstring_id', BigIntegerType, ForeignKey('vocabstrings.vocabstring_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_VICTIMTARGETING_PATH = Table('rel_victimtargeting_path', getattr(Base, 'metadata'),
                                    Column('victimtargeting_id', BigIntegerType, ForeignKey('victimtargetings.victimtargeting_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDCOA_PATH = Table('rel_relatedcoa_path', getattr(Base, 'metadata'),
                                    Column('relatedcoa_id', BigIntegerType, ForeignKey('relatedcoas.relatedcoa_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_PACKAGEINTENT_PATH = Table('rel_packageintent_path', getattr(Base, 'metadata'),
                                    Column('packageintent_id', BigIntegerType, ForeignKey('packageintents.packageintent_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INFORMATIONSOURCEROLE_PATH = Table('rel_informationsourcerole_path', getattr(Base, 'metadata'),
                                    Column('informationsourcerole_id', BigIntegerType, ForeignKey('informationsourceroles.informationsourcerole_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_INDICATORTYPE_PATH = Table('rel_indicatortype_path', getattr(Base, 'metadata'),
                                    Column('indicatortype_id', BigIntegerType, ForeignKey('indicatortypes.indicatortype_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_TARGETEDINFORMATION_PATH = Table('rel_targetedinformation_path', getattr(Base, 'metadata'),
                                    Column('targetedinformation_id', BigIntegerType, ForeignKey('targetedinformations.targetedinformation_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EFFECT_PATH = Table('rel_effect_path', getattr(Base, 'metadata'),
                                    Column('effect_id', BigIntegerType, ForeignKey('effects.effect_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDINDICATOR_PATH = Table('rel_relatedindicator_path', getattr(Base, 'metadata'),
                                    Column('relatedindicator_id', BigIntegerType, ForeignKey('relatedindicators.relatedindicator_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_THREATACTOR_PATH = Table('rel_threatactor_path', getattr(Base, 'metadata'),
                                    Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_DTWP_PATH = Table('rel_datetimewithprecision_path', getattr(Base, 'metadata'),
                                    Column('datetimewithprecision_id', BigIntegerType, ForeignKey('datetimewithprecisions.datetimewithprecision_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_EXTERNALID_PATH = Table('rel_externalid_path', getattr(Base, 'metadata'),
                                    Column('externalid_id', BigIntegerType, ForeignKey('externalids.externalid_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDTTP_PATH = Table('rel_relatedttp_path', getattr(Base, 'metadata'),
                                    Column('relatedttp_id', BigIntegerType, ForeignKey('relatedttps.relatedttp_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_MOTIVATION_PATH = Table('rel_motivation_path', getattr(Base, 'metadata'),
                                    Column('motivation_id', BigIntegerType, ForeignKey('motivations.motivation_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_NPDC_PATH = Table('rel_nonpublicdatacompromised_path', getattr(Base, 'metadata'),
                                    Column('nonpublicdatacompromised_id', BigIntegerType, ForeignKey('nonpublicdatacompromiseds.nonpublicdatacompromised_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_ATTACKPATTERN_PATH = Table('rel_attackpattern_path', getattr(Base, 'metadata'),
                                    Column('attackpattern_id', BigIntegerType, ForeignKey('attackpatterns.attackpattern_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_RELATEDCAMPAIGN_PATH = Table('rel_relatedcampaign_path', getattr(Base, 'metadata'),
                                    Column('relatedcampaign_id', BigIntegerType, ForeignKey('relatedcampaigns.relatedcampaign_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

_REL_SNORTRULE_PATH = Table('rel_snortrule_path', getattr(Base, 'metadata'),
                                    Column('snortrule_id', BigIntegerType, ForeignKey('snortrules.snortrule_id', ondelete='cascade', onupdate='cascade'), nullable=False, primary_key=True, index=True),
                                    Column('path_id', BigIntegerType, ForeignKey('paths.path_id', onupdate='cascade', ondelete='cascade'), nullable=False, primary_key=True, index=True)
                                    )

class Path(BaseObject, Base):

  uuid = None

  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False, index=True)
  item_tlp_level_id = Column('item_tlp_level_id', Integer, default=3, nullable=False, index=True)
  path = Column('path', UnicodeTextType, nullable=False)
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=True, index=True)
  event = relationship(Event, uselist=False)
  dbcode = Column('code', Integer, nullable=False, default=0, index=True)
  item_dbcode = Column('item_code', Integer, nullable=False, default=0, index=True)
  __item_bit_code = None
  __merged_bit_code = None


  @property
  def merged_properties(self):
    """
    Property for the bit_value
    """
    if self.__merged_bit_code is None:
      if self.dbcode is None:
        self.__merged_bit_code = Properties('0', self)
      else:
        self.__merged_bit_code = Properties(self.dbcode, self)
    return self.__merged_bit_code

  @property
  def item_properties(self):
    """
    Property for the bit_value
    """
    if self.__item_bit_code is None:
      if self.dbcode is None:
        self.__item_bit_code = Properties('0', self)
      else:
        self.__item_bit_code = Properties(self.dbcode, self)
    return self.__item_bit_code

  @property
  def parent_table(self):
    splitted = self.path.rsplit('/', 2)
    if len(splitted) == 3:
      instance_code = splitted[1]
      instance_class_code = instance_code.split('-') [0]
      for table_name in getattr(Base, 'metadata').tables.iterkeys():
        class_code = table_code(table_name)
        if not table_name.startswith('rel_') and instance_class_code == class_code:
          return table_name
    else:
      return None

  @property
  def root(self):
    return self.event

