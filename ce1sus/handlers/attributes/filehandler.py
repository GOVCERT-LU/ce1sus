# -*- coding: utf-8 -*-

"""
module handing the filehandler

Created: Aug 22, 2013
"""
import base64
import cherrypy
from cherrypy.lib.static import serve_file
from datetime import datetime
from os import makedirs
from os import remove
from os.path import isfile, getsize, basename, exists, dirname
from shutil import move, rmtree
import types
import zipfile

from ce1sus.common.checks import can_user_download
from ce1sus.db.classes.common import ValueTable
from ce1sus.handlers.base import HandlerException
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.helpers.common.config import ConfigException
from ce1sus.helpers.common.hash import hashMD5
import ce1sus.helpers.common.hash as hasher
from ce1sus.db.classes.object import RelatedObject
import magic


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


CHK_SUM_FILE_NAME = '6582915e9e791da6785cd51232129824640ec967'
CHK_SUM_HASH_SHA1 = '43493cca725be2c4e868cc79d9528eda89d22a3d'
CHK_SUM_HASH_SHA256 = 'fb1f51c9d83919ecec54cfc2dc9bd04214f83155'
CHK_SUM_HASH_SHA384 = 'f0c1d67d19aa775a37aff0b10c714ab9314a13a3'
CHK_SUM_HASH_SHA512 = '78bc5b3d0e7075f86fc461eb3806ecc82fd5e0c0'
CHK_SUM_SIZE_IN_BYTES = 'f0533be2aab3335119f224cccab31e75854fe2cf'
CHK_SUM_MAGIC_NUMBER = 'c40aa7731fbced249920f5737d811c7f4cf570b6'
CHK_SUM_MIME_TYPE = '0bc1a4b87f2df56c0e400883a71d5dfcb331f291'
CHK_SUM_FILE_ID = 'e81cdce63d1c4fd020c929b2ff91da92f5ce14c3'
CHK_SUM_HASH_MD5 = 'a6922165d23112a361f76cd4a5e076cae1e9226f'
CHK_SUM_ARTEFACT = 'aa778b50a158bc996419912e96c1852b2ba59623'


class FileHandler(GenericHandler):
    """Handler for handling files"""

    URLSTR = '/events/event/attribute/call_handler_get/{0}/{1}/{2}'

    @staticmethod
    def get_uuid():
        return '0be5e1a0-8dec-11e3-baa8-0800200c9a66'

    @staticmethod
    def get_allowed_types():
        return [ValueTable.STRING_VALUE]

    def get_additinal_attribute_chksums(self):
        return [CHK_SUM_FILE_NAME, CHK_SUM_HASH_SHA1]

    def get_additional_object_chksums(self):
        return [CHK_SUM_ARTEFACT]

    @staticmethod
    def get_description():
        return u'File handler with only one hash, used for the average file'

    def get_view_type(self):
        return 'file'

    def get_base_path(self):
        """
        Returns the base path for files (as specified in the configuration)
        """
        try:
            config = self.get_config_value('files', None)
            if config:
                return config
            else:
                raise HandlerException(u'Value files in handler configuration for {0} is not set'.format(self.__class__.__name__))
        except ConfigException as error:
            raise HandlerException(error)

    def get_dest_folder(self, rel_folder):
        """
        Returns the destination folder, and creates it when not existing
        """
        try:
            dest_path = self.get_base_path() + '/' + rel_folder
            if not exists(dest_path):
                makedirs(dest_path)
            return dest_path
        except TypeError as error:
            raise HandlerException(error)

    def get_tmp_folder(self):
        """
        Returns the temporary folder, and creates it when not existing
        """
        try:
            tmp_path = self.get_base_path() + '/tmp/' + hasher.hashSHA1('{0}'.format(datetime.utcnow()))
            if not exists(tmp_path):
                makedirs(tmp_path)
            return tmp_path
        except TypeError as error:
            raise HandlerException(error)

    def insert(self, obj, user, json):
        value = json.get('value', None)
        filename = value.get('name', None)
        data = value.get('data', None)
        if isinstance(data, types.DictionaryType):
            # Workaround for the webfront end
            data = data.get('data', None)

        if filename and data:
            # save file to tmp folder
            tmp_filename = hashMD5(datetime.utcnow())
            binary_data = base64.b64decode(data)
            tmp_folder = self.get_tmp_folder()
            tmp_path = tmp_folder + '/' + tmp_filename

            # create file in tmp
            file_obj = open(tmp_path, "w")
            file_obj.write(binary_data)
            file_obj.close

            sha1 = hasher.fileHashSHA1(tmp_path)
            rel_folder = self.get_rel_folder()
            dest_path = self.get_dest_folder(rel_folder) + '/' + sha1

            # move it to the correct place
            move(tmp_path, dest_path)
            # remove temp folder
            rmtree(dirname(tmp_path))

            # create attribtues
            internal_json = json
            # main
            main_definition = self.get_main_definition()

            internal_json['value'] = rel_folder + '/' + sha1

            attributes = list()

            main_attribute = self.create_attribute(obj, main_definition, user, internal_json)

            # secondary

            filename_definition = self.get_attriute_definition(CHK_SUM_FILE_NAME)
            internal_json['value'] = filename
            attribute = self.create_attribute(obj, filename_definition, user, internal_json)
            attributes.append(attribute)

            sha1_definition = self.get_attriute_definition(CHK_SUM_HASH_SHA1)
            internal_json['value'] = sha1
            attribute = self.create_attribute(obj, sha1_definition, user, internal_json)
            attributes.append(attribute)

            # set parent
            for attribtue in attributes:
                attribtue.parent = main_attribute

            obj_def = self.get_object_definition(CHK_SUM_ARTEFACT)
            childobj = self.create_object(obj.observable, obj_def, user, {}, False)

            rel_obj = RelatedObject()
            rel_obj.parent = obj
            rel_obj.parent_id = obj.identifier
            rel_obj.object = childobj

            childobj.attributes.append(main_attribute)
            # attributes.append(main_attribute)

            childobjs = list()
            childobjs.append(rel_obj)

            return attributes, childobjs

        else:
            raise HandlerException('Value is invalid format has to be {"name": <name>,"data": <base 64 encoded data> }')

    def update(self, attribute, user, json):
        raise HandlerException('FileHandler does not support updates')

    def get_data(self, attribute, definition, parameters):
        if attribute:
            rel_path = attribute.value
            event = attribute.object.event

            user_can_download = can_user_download(event, self.user)
            if not user_can_download:
                raise cherrypy.HTTPError(status=403, message='User is not permitted to download files')
            base_path = self.get_base_path()
            if base_path and rel_path:
                filepath = base_path + '/' + rel_path
                if isfile(filepath):
                    filename = self.__get_orig_filename(attribute)
                    # create zipfile
                    tmp_path = self.get_base_path()
                    if not filename:
                        filename = basename(filepath)
                    tmp_path += '/' + basename(filepath) + '.zip'
                    # remove file if it should exist
                    try:
                        remove(tmp_path)
                    except OSError:
                        pass
                    # create zip file
                    zip_file = zipfile.ZipFile(tmp_path, mode='w')
                    # TODO: set password for zip file
                    zip_file.write(filepath, arcname=filename)
                    zip_file.close()
                    filename = u'{0}.zip'.format(filename)
                    filename = filename.encode('utf-8')
                    result = serve_file(tmp_path, "application/x-download", "attachment", name=filename)
                    # clean up
                    try:
                        remove(tmp_path)
                    except OSError:
                        pass
                    return result
                else:
                    raise HandlerException('The file was not found in "{0}"'.format(filepath))
            else:
                raise HandlerException('There was an error getting the file')
        else:
            return list()

    @staticmethod
    def _get_dest_filename(file_hash, file_name):
        """
        Returns the file name of the destination
        """
        hashed_file_name = hasher.hashSHA256(file_name)
        key = '{0}{1}{2}'.format(file_hash,
                                 datetime.utcnow(),
                                 hashed_file_name)
        return hasher.hashSHA256(key)

    def get_rel_folder(self):
        """
        Returns the string of the relative folder position
        """
        dest_path = '{0}/{1}/{2}'.format(datetime.utcnow().year,
                                         datetime.utcnow().month,
                                         datetime.utcnow().day)
        return dest_path

    def __get_orig_filename(self, attribtue):
        """
        Returns the original filename
        """
        if attribtue.children:
            for child in attribtue.children:
                if child.definition.chksum == CHK_SUM_FILE_NAME:
                    return child.plain_value
            # ok no filename has been found using the one from the attribute value
            return basename(attribtue.value)
        else:
            # get parent object
            if attribtue.object.related_object_parent and attribtue.object.related_object_parent[0].parent:
                for attribtue in attribtue.object.related_object_parent and attribtue.object.related_object_parent[0].parent.attributes:
                    if attribtue.definition.chksum == CHK_SUM_FILE_NAME:
                        return attribtue.value

            return None


class FileWithHashesHandler(FileHandler):
    """
    Extends the filehandler with additional hashes
    """
    @staticmethod
    def get_uuid():
        return 'e8b47b60-8deb-11e3-baa8-0800200c9a66'

    def get_additinal_attribute_chksums(self):
        return [CHK_SUM_FILE_NAME,
                CHK_SUM_HASH_SHA1,
                CHK_SUM_HASH_SHA256,
                CHK_SUM_HASH_SHA384,
                CHK_SUM_HASH_SHA512,
                CHK_SUM_SIZE_IN_BYTES,
                CHK_SUM_MAGIC_NUMBER,
                CHK_SUM_MIME_TYPE,
                CHK_SUM_FILE_ID,
                CHK_SUM_HASH_MD5]

    def insert(self, obj, user, json):
        attributes, sub_objects = super(FileWithHashesHandler, self).insert(obj, user, json)

        internal_json = json
        main_attribute = sub_objects[0].object.attributes[0]

        filepath = self.get_base_path() + '/' + main_attribute.value

        # create the remaining attributes
        internal_json['value'] = hasher.fileHashMD5(filepath)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_MD5), user, internal_json)
        attributes.append(attribute)

        internal_json['value'] = hasher.fileHashSHA256(filepath)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_SHA256), user, internal_json)
        attributes.append(attribute)

        internal_json['value'] = hasher.fileHashSHA384(filepath)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_SHA384), user, internal_json)
        attributes.append(attribute)

        internal_json['value'] = hasher.fileHashSHA512(filepath)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_HASH_SHA512), user, internal_json)
        attributes.append(attribute)

        internal_json['value'] = getsize(filepath)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_SIZE_IN_BYTES), user, internal_json)
        attributes.append(attribute)

        internal_json['value'] = magic.from_file(filepath, mime=True)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_MIME_TYPE), user, internal_json)
        attributes.append(attribute)

        internal_json['value'] = magic.from_file(filepath)
        attribute = self.create_attribute(obj, self.get_attriute_definition(CHK_SUM_FILE_ID), user, internal_json)
        attributes.append(attribute)

        # set parent
        for attribtue in attributes:
            attribtue.parent = main_attribute

        return attributes, sub_objects

    def require_js(self):
        return False
