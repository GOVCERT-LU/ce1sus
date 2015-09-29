# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 26, 2015
"""


from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.relations import _REL_IDENTITY_RELATED_IDENTITY, _REL_INFORMATIONSOURCE_IDENTITY
from ce1sus.db.classes.cstix.incident.relations import _REL_INCIDENT_IDENTITY
from ce1sus.db.classes.cstix.threat_actor.relations import _REL_THREATACTOR_IDENTITY
from ce1sus.db.classes.cstix.ttp.relations import _REL_VICTIMTARGETING_IDENTITY
from ce1sus.db.classes.cstix.ttp.resource import _REL_RESOURCE_IDENTITIY
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Identity(Entity, Base):
  """NOTE this is not used to represent information provides etc only for internal representations"""

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['information_source',
              'resource',
              'victim_targeting',
              'threat_actor',
              'incident',
              'related_identity']

  incident = relationship('Incident', secondary=_REL_INCIDENT_IDENTITY, uselist=False)
  threat_actor = relationship('ThreatActor', secondary=_REL_THREATACTOR_IDENTITY, uselist=False)
  victim_targeting = relationship('VictimTargeting', secondary=_REL_VICTIMTARGETING_IDENTITY, uselist=False)
  information_source = relationship('InformationSource', uselist=False, secondary=_REL_INFORMATIONSOURCE_IDENTITY)
  related_identity = relationship('RelatedIdentity', uselist=False, primaryjoin='RelatedIdentity.child_id==Identity.identifier')
  resource = relationship('Resource', uselist=False, secondary=_REL_RESOURCE_IDENTITIY)

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  idref = Column('idref', UnicodeType(45), nullable=True, index=True)
  name = Column('name', UnicodeType(255), index=True, nullable=True)
  related_identities = relationship('RelatedIdentity', secondary=_REL_IDENTITY_RELATED_IDENTITY)


  def get_populated(self, cache_object):
    return self.get_instance([Identity.related_identities], cache_object)

  def to_dict(self, cache_object):
    instance = self.get_populated(cache_object)
    result = {
              'id_': instance.convert_value(instance.id_),
              'idref': instance.convert_value(instance.idref),
              'name': instance.convert_value(instance.name),
              'related_identities': instance.attributelist_to_dict('related_identities', cache_object)
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
