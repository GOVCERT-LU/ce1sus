# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 7, 2015
"""

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BigInteger, UnicodeText, Unicode, Boolean

from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ErrorMispAttribute(Base):

    object_id = Column('object_id', BigInteger, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'))

    value = Column('value', UnicodeText(collation='utf8_unicode_ci'))
    category = Column('category', Unicode(255, collation='utf8_unicode_ci'))
    type_ = Column('type', Unicode(255, collation='utf8_unicode_ci'))
    observable_id = Column('observable_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'))

    misp_id = Column('misp_id', Unicode(255, collation='utf8_unicode_ci'))
    is_ioc = Column('is_ioc', Boolean)
    share = Column('share', Boolean)

    event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'))
    message = Column('message', UnicodeText(collation='utf8_unicode_ci'))
    orig_uuid = Column('orig_uuid', Unicode(45, collation='utf8_unicode_ci'))

    def validate(self):
        return True
