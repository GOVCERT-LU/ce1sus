-- MySQL dump 10.13  Distrib 5.5.34, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: ce1sus_jhemp_dev
-- ------------------------------------------------------
-- Server version	5.5.31-0+wheezy1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Attribute_Object_Relations`
--

DROP TABLE IF EXISTS `Attribute_Object_Relations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Attribute_Object_Relations` (
  `AOR_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ref_attribute_id` bigint(20) NOT NULL,
  `attribute_id` bigint(20) NOT NULL,
  `ref_object_id` bigint(20) NOT NULL,
  PRIMARY KEY (`AOR_id`),
  UNIQUE KEY `UNQ_AOR_attribID_refAttribID` (`ref_object_id`,`ref_attribute_id`),
  KEY `IDX_AOR_Attribtues_ref_attribute_id` (`ref_attribute_id`),
  KEY `IDX_AOR_Attribtues_attribute_id` (`attribute_id`),
  KEY `IDX_AOR_Objects_obejct_id` (`ref_object_id`),
  CONSTRAINT `FK_AOR_Attribtues_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_AOR_Attribtues_ref_attribute_id` FOREIGN KEY (`ref_attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_AOR_Objects_obejct_id` FOREIGN KEY (`ref_object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1 COMMENT='The ref_object_id is just to keep the relations unique to pr';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Attributes`
--

DROP TABLE IF EXISTS `Attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Attributes` (
  `attribute_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `def_attribute_id` bigint(20) NOT NULL,
  `object_id` bigint(20) NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `modifier_id` bigint(20) DEFAULT NULL,
  `created` datetime NOT NULL,
  `modified` datetime DEFAULT NULL,
  `ioc` int(1) NOT NULL DEFAULT '0',
  `code` int(1) DEFAULT NULL,
  PRIMARY KEY (`attribute_id`),
  KEY `IDX_attr_def_attribute_id` (`def_attribute_id`),
  KEY `IDX_attr_object_id` (`object_id`),
  KEY `IDX_Attr_Objects_object_id` (`object_id`),
  KEY `IDX_Attr_creator_id` (`creator_id`),
  KEY `IDX_Attr_modifier_id` (`modifier_id`),
  KEY `IDX_Attr_id_sharable` (`attribute_id`),
  CONSTRAINT `FK_Attr_DAttr_attribute_id` FOREIGN KEY (`def_attribute_id`) REFERENCES `DEF_Attributes` (`def_attribute_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Attr_Objects_object_id` FOREIGN KEY (`object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Attr_Users_creator_id_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Attr_Users_modifier_id_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Comments`
--

DROP TABLE IF EXISTS `Comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Comments` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) NOT NULL,
  `comment` mediumtext,
  `created` datetime NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `modifier_id` bigint(20) DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `IDX_comments_event_id` (`event_id`),
  KEY `IDX_Comments_User_creator_user_id` (`creator_id`),
  KEY `IDX_Comments_User_modifier_user_id` (`modifier_id`),
  CONSTRAINT `FK_Comments_User_creator_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Comments_User_modifier_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_events_comments_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DEF_Attributes`
--

DROP TABLE IF EXISTS `DEF_Attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DEF_Attributes` (
  `def_attribute_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` mediumtext NOT NULL,
  `regex` varchar(255) NOT NULL DEFAULT '^.*$',
  `classIndex` int(11) NOT NULL DEFAULT '0',
  `handlerIndex` int(11) NOT NULL DEFAULT '0',
  `deletable` int(1) NOT NULL DEFAULT '1',
  `sharable` int(1) NOT NULL DEFAULT '0',
  `relationable` int(1) NOT NULL DEFAULT '0',
  `chksum` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`def_attribute_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_attributes_name` (`name`),
  KEY `IDX_def_attributes_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DEF_Attributes`
--

LOCK TABLES `DEF_Attributes` WRITE;
/*!40000 ALTER TABLE `DEF_Attributes` DISABLE KEYS */;
INSERT INTO `DEF_Attributes` (`def_attribute_id`, `name`, `description`, `regex`, `classIndex`, `handlerIndex`, `deletable`, `sharable`, `relationable`, `chksum`) VALUES (1,'File (Malicious)','File','^.+$',1,1,0,1,0,'fd7c87b3c05ddf3183375ec1d5fb4220f9bc13f2'),(2,'md5','The MD5 value specifies the MD5 hashing algorithm.','^[0-9a-fA-F]{32}$',1,5,0,1,1,'3b7c6838e40dde1153b72c28c01184750e2b028f'),(3,'sha1','The SHA1 value specifies the SHA1 hashing algorithm.','^[0-9a-fA-F]{40}$',1,5,0,1,1,'da60fc54825de884331160cf8a8ba63429ccae32'),(4,'sha256','The SHA256 value specifies the SHA256 hashing algorithm.','^[0-9a-fA-F]{64}$',1,5,0,1,1,'9b658f3f8752ff96c449e2ab97ebadbfed6c1e91'),(5,'sha384','The SHA384 value specifies the SHA384 hashing algorithm.','^[0-9a-fA-F]{96}$',1,5,0,1,1,'db28cf635524e2c51f9a924177ffb448d190021a'),(6,'sha512','The SHA512 value specifies the SHA512 hashing algorithm.','^[0-9a-fA-F]{128}$',1,5,0,1,1,'de6ca0fc697061c91e8ad22397182e43b628d879'),(7,'filename','Filename','^.+$',1,0,0,1,1,'8f1661566860b1ea67915ad7b1644401ca4ff2dc'),(8,'size','File size','^[\\d]{1,}$',3,0,0,1,0,'f678837ff0319736149d9f3b5d008e29ae155d5f'),(9,'mimeType','Mime type of a file','^.+$',1,0,0,1,0,'ac848410bab532a8a227ac10c33f579b98f7b36f'),(10,'Internal_reference','Internal reference','^[\\d]{5,}$',3,2,0,1,1,'077b1864cd323c6442307db28441971c6aa8db79'),(11,'CVE','CVE reference','^CVE-(19|20)\\d{2}-[\\d]{4}$',1,3,0,1,1,'8233d8321c4e3313517f398967e7fdd2f4c4252d'),(12,'File (UnMalicious)','File','^.+$',1,1,0,1,0,'4e72f45aa5ff7c3d5bd21712dc5a1aac36242cd5'),(28,'hostname','fwdn','^.*$',1,0,1,0,1,'074dcc590794ea58c3ec1934e1f80b61b7e0ce38');
/*!40000 ALTER TABLE `DEF_Attributes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DEF_Objects`
--

DROP TABLE IF EXISTS `DEF_Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DEF_Objects` (
  `def_object_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` mediumtext,
  `chksum` varchar(45) DEFAULT NULL,
  `sharable` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`def_object_id`),
  UNIQUE KEY `chksum_UNIQUE` (`chksum`),
  KEY `IDX_def_objects_chksum` (`chksum`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DObj_has_DAttr`
--

DROP TABLE IF EXISTS `DObj_has_DAttr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DObj_has_DAttr` (
  `def_object_id` bigint(20) NOT NULL,
  `def_attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`def_object_id`,`def_attribute_id`),
  KEY `IDX_DOhDA_def_object_id` (`def_attribute_id`),
  KEY `IDX_DOhDA_def_attribute_id` (`def_object_id`),
  CONSTRAINT `FK_DAttrs_DObjs_DAttrID` FOREIGN KEY (`def_attribute_id`) REFERENCES `DEF_Attributes` (`def_attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_DObjs_DAttrs_DOId` FOREIGN KEY (`def_object_id`) REFERENCES `DEF_Objects` (`def_object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DateValues`
--

DROP TABLE IF EXISTS `DateValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DateValues` (
  `DateValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` datetime DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`DateValue_id`),
  KEY `IDX_DateValues_attribute_id` (`attribute_id`),
  KEY `IDX_DateValues_Value` (`value`),
  CONSTRAINT `FK_DateValues_Attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Events`
--

DROP TABLE IF EXISTS `Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Events` (
  `event_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `description` text,
  `title` varchar(255) DEFAULT NULL,
  `created` datetime NOT NULL,
  `first_seen` datetime NOT NULL,
  `last_seen` datetime DEFAULT NULL,
  `modified` datetime DEFAULT NULL,
  `published` tinyint(1) NOT NULL DEFAULT '0',
  `status_id` int(11) NOT NULL DEFAULT '0',
  `tlp_level_id` int(1) NOT NULL DEFAULT '3',
  `risk_id` int(11) NOT NULL,
  `analysis_status_id` int(11) NOT NULL,
  `creator_id` bigint(20) NOT NULL,
  `modifier_id` bigint(20) DEFAULT NULL,
  `uuid` varchar(45) DEFAULT NULL,
  `creatorGroup` int(11) NOT NULL,
  `code` int(1) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `IDX_Events_uuid` (`uuid`),
  KEY `IDK_Events_creator_id` (`creator_id`),
  KEY `IDX_Events_modifier_ID` (`modifier_id`),
  KEY `IDX_Events_creatorGroup` (`creatorGroup`),
  CONSTRAINT `FK_Events_Groups_creator` FOREIGN KEY (`creatorGroup`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_creator_user_ID` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_User_modifier_user_ID` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Events_has_Objects`
--

DROP TABLE IF EXISTS `Events_has_Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Events_has_Objects` (
  `event_id` bigint(20) NOT NULL,
  `object_id` bigint(20) NOT NULL,
  PRIMARY KEY (`event_id`,`object_id`),
  KEY `IDX_EhO_event_id` (`object_id`),
  KEY `IDX_EhO_object_id` (`event_id`),
  CONSTRAINT `fk_Eho_Event_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Eho_Object_object_id` FOREIGN KEY (`object_id`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Groups`
--

DROP TABLE IF EXISTS `Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `description` mediumtext,
  `canDownlad` int(1) NOT NULL DEFAULT '0',
  `tlplvl` int(1) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `usermails` int(1) NOT NULL DEFAULT '0',
  `pgpKey` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  KEY `IDK_Groups_tlplvl` (`tlplvl`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Groups`
--

LOCK TABLES `Groups` WRITE;
/*!40000 ALTER TABLE `Groups` DISABLE KEYS */;
INSERT INTO `Groups` (`group_id`, `name`, `description`, `canDownlad`, `tlplvl`, `email`, `usermails`, `pgpKey`) VALUES (1,'Default_Group','Default Group, for all users',0,3,'a@a.com',0,NULL);
/*!40000 ALTER TABLE `Groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Groups_has_Events`
--

DROP TABLE IF EXISTS `Groups_has_Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups_has_Events` (
  `group_id` int(11) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  PRIMARY KEY (`group_id`,`event_id`),
  KEY `IDX_GhE_group_id` (`event_id`),
  KEY `IDX_GhE_event_id` (`group_id`),
  CONSTRAINT `FK_Events_Groups_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Groups_Events_Group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `NumberValues`
--

DROP TABLE IF EXISTS `NumberValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `NumberValues` (
  `NumberValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` decimal(10,0) DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`NumberValue_id`),
  KEY `IDX_numberValue_attribute_id` (`attribute_id`),
  KEY `IDX_NumberValue_value` (`value`),
  CONSTRAINT `fk_NumberValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Obj_links_Obj`
--

DROP TABLE IF EXISTS `Obj_links_Obj`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Obj_links_Obj` (
  `object_id_to` bigint(20) NOT NULL,
  `object_id_from` bigint(20) NOT NULL,
  PRIMARY KEY (`object_id_to`,`object_id_from`),
  KEY `IDX_OlO_from` (`object_id_from`),
  KEY `IDX_OlO_to` (`object_id_to`),
  CONSTRAINT `FK_Olo_Obj_object_id_from` FOREIGN KEY (`object_id_from`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Olo_Obj_object_id_to` FOREIGN KEY (`object_id_to`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Objects`
--

DROP TABLE IF EXISTS `Objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Objects` (
  `object_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `creator_id` bigint(20) NOT NULL,
  `def_object_id` bigint(20) NOT NULL,
  `event_id` bigint(20) DEFAULT NULL,
  `created` datetime NOT NULL,
  `parentObject` bigint(20) DEFAULT NULL,
  `parentEvent` bigint(20) DEFAULT NULL,
  `code` int(1) NOT NULL DEFAULT '0',
  `modifier_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`object_id`),
  KEY `IDX_DObj_objects_def_object_id` (`def_object_id`),
  KEY `IDX_objects_events_event_id` (`event_id`),
  KEY `IDX_object_object_object_id` (`parentObject`),
  KEY `IDX_objects_events_event_id_parentEvent` (`parentEvent`),
  KEY `IDX_Obj_creator_id` (`creator_id`),
  KEY `IDX_Obj_modifier_id` (`modifier_id`),
  KEY `IDX_obj_id_shareable` (`object_id`),
  CONSTRAINT `FK_DObj_objects_def_object_id` FOREIGN KEY (`def_object_id`) REFERENCES `DEF_Objects` (`def_object_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_objects_events_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_objects_events_event_id_parentEvent` FOREIGN KEY (`parentEvent`) REFERENCES `Events` (`event_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_object_object_object_id` FOREIGN KEY (`parentObject`) REFERENCES `Objects` (`object_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_Obj_user_creator_id_user_id` FOREIGN KEY (`creator_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Obj_user_modifier_id_user_id` FOREIGN KEY (`modifier_id`) REFERENCES `Users` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `StringValue`
--

DROP TABLE IF EXISTS `StringValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `StringValues` (
  `StringValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` varchar(255) DEFAULT NULL,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`StringValue_id`),
  KEY `IDX_StrValues_attr_id` (`attribute_id`),
  KEY `IDX_StrValue_Value` (`value`),
  CONSTRAINT `fk_StringValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=676 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SubGroups_has_Events`
--

DROP TABLE IF EXISTS `SubGroups_has_Events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SubGroups_has_Events` (
  `subgroup_id` int(11) NOT NULL,
  `event_id` bigint(20) NOT NULL,
  PRIMARY KEY (`subgroup_id`,`event_id`),
  KEY `IDX_EhS_subgroup_id` (`subgroup_id`),
  KEY `IDX_EhS_event_id` (`event_id`),
  CONSTRAINT `FK_Events_SubGroups_event_id` FOREIGN KEY (`event_id`) REFERENCES `Events` (`event_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SUBGroups_Events_subgroup_id` FOREIGN KEY (`subgroup_id`) REFERENCES `Subgroups` (`subgroup_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Subgroups`
--

DROP TABLE IF EXISTS `Subgroups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Subgroups` (
  `subgroup_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(255) NOT NULL,
  PRIMARY KEY (`subgroup_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Subgroups_has_Groups`
--

DROP TABLE IF EXISTS `Subgroups_has_Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Subgroups_has_Groups` (
  `subgroup_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`subgroup_id`,`group_id`),
  KEY `IDX_subgroups_groups_group_id` (`group_id`),
  KEY `IDX_subgroups_groups_subgroup_id` (`subgroup_id`),
  CONSTRAINT `fk_subgroups_groups_group_id` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_subgroups_groups_subgroup_id` FOREIGN KEY (`subgroup_id`) REFERENCES `Subgroups` (`subgroup_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TextValues`
--

DROP TABLE IF EXISTS `TextValues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TextValues` (
  `TextValue_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `value` longtext,
  `attribute_id` bigint(20) NOT NULL,
  PRIMARY KEY (`TextValue_id`),
  KEY `IDX_TextValues_attribute_id` (`attribute_id`),
  CONSTRAINT `FK_TextValues_attr_attribute_id` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Users` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL COMMENT '	\n',
  `password` varchar(255) NOT NULL,
  `privileged` int(1) DEFAULT '0',
  `last_login` datetime DEFAULT NULL,
  `email` varchar(45) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL,
  `disabled` int(1) NOT NULL DEFAULT '1',
  `apikey` varchar(255) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `pgpKey` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `apikey_UNIQUE` (`apikey`),
  KEY `fk_users_groups_mainGroup` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` (`user_id`, `username`, `password`, `privileged`, `last_login`, `email`, `disabled`, `apikey`, `group_id`, `pgpKey`) VALUES (1,'admin','dd94709528bb1c83d08f3088d4043f4742891f4f',1,'2013-11-20 13:43:14','admin@admin.com',0,NULL,1,NULL);
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ce1sus`
--

DROP TABLE IF EXISTS `ce1sus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ce1sus` (
  `key` varchar(45) NOT NULL,
  `value` varchar(100) DEFAULT 'None',
  PRIMARY KEY (`key`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ce1sus`
--

LOCK TABLES `ce1sus` WRITE;
/*!40000 ALTER TABLE `ce1sus` DISABLE KEYS */;
INSERT INTO `ce1sus` (`key`, `value`) VALUES ('app_rev','0.2.2'),('db_shema','0.3.0'),('rest_api','0.1.0');
/*!40000 ALTER TABLE `ce1sus` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-11-20 14:23:23
