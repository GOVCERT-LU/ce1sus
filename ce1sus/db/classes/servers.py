# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, Integer, Boolean, BigInteger

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import ServerType
from ce1sus.db.common.session import Base
from ce1sus.helpers.bitdecoder import BitBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ServerMode(BitBase):

    """
    The __bit_value is defined as follows:
    [0] : Is validated
    [1] : Is sharable - On event lvl it has the same meaning as published
    [2] : Is proposal
    """
    # 1
    PULL = 0
    # 2
    PUSH = 1

    @property
    def is_push(self):
        return self._get_value(ServerMode.PULL)

    @is_push.setter
    def is_push(self, value):
        self._set_value(ServerMode.PULL, value)

    @property
    def is_pull(self):
        return self._get_value(ServerMode.PUSH)

    @is_pull.setter
    def is_pull(self, value):
        self._set_value(ServerMode.PUSH, value)

    def to_dict(self):
        return {'is_pull': self.is_pull,
                'is_push': self.is_push
                }

    def populate(self, json):
        self.is_pull = json.get('is_pull', False)
        self.is_push = json.get('is_push', False)


class SyncServer(ExtendedLogingInformations, Base):

    name = Column('name', Unicode(255, collation='utf8_unicode_ci'))
    user_id = Column('user_id', BigInteger, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), index=True, unique=True)
    user = relationship('User', primaryjoin='SyncServer.user_id==User.identifier')
    baseurl = Column('baseurl', Unicode(255, collation='utf8_unicode_ci'), index=True)
    mode_code = Column('mode_id', Integer, index=True, default=0)
    type_id = Column('type_id', Integer, index=True)
    description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
    certificate = Column('certificat', UnicodeText(collation='utf8_unicode_ci'))
    ca_certificate = Column('ca_certificat', UnicodeText(collation='utf8_unicode_ci'))
    verify_ssl = Column('verify_ssl', Boolean)
    __mode_code = None

    @property
    def mode(self):
        if self.mode_code:
            self.__mode_code = ServerMode(self.mode_code, self, 'mode_code')
        else:
            self.__mode_code = ServerMode('0', self, 'mode_code')
        return self.__mode_code

    @mode.setter
    def mode(self, value):
        self.__mode_code = value
        self.mode_code = value.bit_code
        self.__mode_code.parent = self

    @property
    def type(self):
        """
        returns the status

        :returns: String
        """
        return ServerType.get_by_id(self.type_id)

    @type.setter
    def type(self, type_text):
        """
        returns the status

        :returns: String
        """
        self.type_id = ServerType.get_by_value(type_text)

    def to_dict(self, complete=True, inflated=False):
        if self.user_id:
            user = self.user.to_dict(complete, False)
            user_id = self.user.uuid
        else:
            user = None
            user_id = None

        if complete:
            return {'identifier': self.convert_value(self.uuid),
                    'name': self.convert_value(self.name),
                    'description': self.convert_value(self.description),
                    'mode': self.mode.to_dict(),
                    'type_id': self.convert_value(self.description),
                    'type': self.convert_value(self.type),
                    'baseurl': self.convert_value(self.baseurl),
                    'certificate': self.convert_value(self.certificate),
                    'ca_certificate': self.convert_value(self.ca_certificate),
                    'verify_ssl': self.convert_value(self.verify_ssl),
                    'user': user,
                    'user_id': user_id,
                    }
        else:
            return {'identifier': self.uuid,
                    'name': self.name
                    }

    def populate(self, json):
        self.name = json.get('name', None)
        self.description = json.get('description', None)
        self.type_id = json.get('type_id', None)
        self.baseurl = json.get('baseurl', None)
        self.baseurl = json.get('baseurl', None)
        self.api_key = json.get('api_key', None)
        self.certificate = json.get('certificate', None)
        self.ca_certificate = json.get('ca_certificate', None)
        self.verify_ssl = json.get('verify_ssl', False)
        # permissions setting
        self.mode.populate(json.get('mode', {}))
        # TODO add group

    def validate(self):
        # TODO implement validate
        return True
