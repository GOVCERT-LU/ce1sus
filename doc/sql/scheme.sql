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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='The ref_object_id is just to keep the relations unique to pr';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Attribute_Object_Relations`
--

LOCK TABLES `Attribute_Object_Relations` WRITE;
/*!40000 ALTER TABLE `Attribute_Object_Relations` DISABLE KEYS */;
/*!40000 ALTER TABLE `Attribute_Object_Relations` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Attributes`
--

LOCK TABLES `Attributes` WRITE;
/*!40000 ALTER TABLE `Attributes` DISABLE KEYS */;
/*!40000 ALTER TABLE `Attributes` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Comments`
--

LOCK TABLES `Comments` WRITE;
/*!40000 ALTER TABLE `Comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `Comments` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=116 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DEF_Attributes`
--

LOCK TABLES `DEF_Attributes` WRITE;
/*!40000 ALTER TABLE `DEF_Attributes` DISABLE KEYS */;
INSERT INTO `DEF_Attributes` (`def_attribute_id`, `name`, `description`, `regex`, `classIndex`, `handlerIndex`, `deletable`, `sharable`, `relationable`, `chksum`) VALUES (29,'hash_md5','md5 hash of a file','^[0-9a-fA-F]{32}$',1,0,1,1,1,'8b5b60262a070b4e86bdeee771df1c5f82af411d'),(30,'hash_sha1','sha1 hash of a file','^[0-9a-fA-F]{40}$',1,0,1,1,1,'071eb20cd80ea3d874dfad489c822a2016daa00d'),(31,'hash_sha256','sha256 hash of a file','^[0-9a-fA-F]{64}$',1,0,1,1,1,'2551d42b10cf0a1716671436b77698f90fed0c27'),(32,'hash_sha384','sha384 hash of a file','^[0-9a-fA-F]{96}$',1,0,1,1,1,'7e44a3ebb32e48e812c3301277e96b695cc0ed89'),(33,'hash_sha512','sha512 hash of a file','^[0-9a-fA-F]{128}$',1,0,1,1,1,'782f49137df2fc3589ff472664036e64621e2b66'),(34,'hash_ssdeep','ssdeep hash of a file','^\\d+:[a-zA-Z0-9+]+:[a-zA-Z0-9+]+$',1,0,1,1,0,'a92dbb7f7bf68020e6fd74b0de2de661c716d128'),(35,'file_name','The file_name field specifies the name of the file.','^.+$',1,0,1,1,0,'9802f41df84b79d361e9aafe62386299a77c76f8'),(36,'size_in_bytes','The size_in_bytes field specifies the size of the file, in bytes.','^\\d+$',3,0,1,1,0,'32c393fd3ea0ea1f5439d5b7e1db310e283a1cc1'),(37,'magic_number','The magic_number specifies the particular magic number (typically a hexadecimal constant used to identify a file format) corresponding to the file, if applicable.','^.+$',1,0,1,1,0,'12764f37a8f9997ebdd5c7f2f4905d4ed17ab1df'),(38,'reference_internal_identifier','Holds a reference to an internal ID number.','^\\d+$',3,2,1,1,0,'c0695d0f2113b426fd5355f49c27979034de2ee3'),(39,'vulnerability_cve','CVE reference to a known vulnerability','^CVE-(19|20)\\d{2}-[\\d]{4}$',1,3,1,1,1,'fd669897a7768fbfd703a2cd033fc48d54f17c83'),(40,'raw_file','The raw file data','^.+$',1,1,1,0,0,'ddb88c41be6b708aaf6309bcfc4bb3762ec387e8'),(41,'raw_document_file','The raw document (non malicious file)','^.+$',1,6,1,1,0,NULL),(42,'hostname','Fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'2376b03d4148c212c63cc1904a04e17b1baa26ac'),(43,'description','Contains free text description for an object','^.+$',0,0,1,1,0,'b248f7d94db2e4da5188d7d8ba242f23ba733012'),(44,'comment','Holds free text for comments about objects and event.','^.+$',0,0,1,0,0,NULL),(45,'is_malicious','Boolean to identify malicious objects','^(yes|no)$',1,8,1,1,0,NULL),(46,'malware_file_type','dropper, trojan, banking trojan, RAT, rogue document, phishing document,....','^.+$',1,0,1,1,0,NULL),(47,'file_full_path','The File path including the file name.','^.+$',1,0,1,1,0,NULL),(48,'file_extension','The File_Extension field specifies the file extension of the file.','^.+$',1,0,1,1,0,NULL),(49,'file_format','The File_Format field specifies the particular file format of the file, most typically specified by a tool such as the UNIX file command.','^.+$',1,0,1,1,0,NULL),(50,'digital_signature','The Digital_Signatures field is optional and captures one or more digital signatures for the file.','^.+$',0,0,1,1,1,'ff6f1e3f3814b88261d6bb4f41710395d89fcd80'),(51,'file_modified_time','The Modified_Time field specifies the date/time the file was last modified.','^.+$',2,7,1,1,0,NULL),(52,'file_accessed_datetime','The Accessed_Time field specifies the date/time the file was last accessed.','^.+$',2,7,1,1,0,NULL),(53,'file_created_datetime','The Created_Time field specifies the date/time the file was created.','^.+$',2,7,1,1,0,NULL),(54,'packer','The Packer_List field specifies any packers that the file may be packed with. The term \'packer\' here refers to packers, as well as things like archivers and installers.','^.+$',1,0,1,1,0,NULL),(55,'peak_entropy','The Peak_Entropy field specifies the calculated peak entropy of the file.','^[\\d]{1,}$',3,0,1,1,0,NULL),(56,'encryption_mechanism','The encryption_mechanism field is optional and specifies the protection/encryption algorithm utilized to protect the Raw_Artifact content.','^.+$',0,0,1,1,0,NULL),(57,'discovery_method','The Discovery_Method field is intended to characterize the method and/or tool used to discover the object.','^.+$',0,0,1,1,0,NULL),(58,'vulnerability_
free_text','Free text description for a vulnerability','^.+$',0,0,1,1,0,NULL),(59,'reference_url','URL pointing to online information','^.+$',1,0,1,1,0,'1aadfbb852f3a7f0011860ac73827b74b092f3a3'),(60,'reference_free_text','Free text used to give reference information.','^.+$',0,0,1,1,0,NULL),(61,'analysis_free_text','A free text analysis for the object.','^.+$',0,0,1,1,0,NULL),(62,'information_source','Free text holding information about the source of an information (e.g where did a document come from).','^.+$',0,0,1,1,0,NULL),(63,'reference_internal_case','Holds a reference to an internal case to which the event is related.','^.+$',1,0,1,1,0,NULL),(64,'reference_external_identifier','Contains an external identifier for the event','^.+$',1,0,1,1,1,'6a83cfd07cb7832ef48a753e305944c3a03b6ebf'),(65,'creation_datetime','The creation time stamp of an object','^.+$',2,7,1,1,0,NULL),(66,'raw_pcap_file','The raw file data','^.+$',1,6,1,1,0,'4235363ecfe479f90e10e1a1140d714ea13d2e42'),(67,'email_attachment_file_name','The Attachments field specifies any files that were attached to the email message. It imports and uses the CybOX FileObjectType from the File_Object to do so.','^.+$',1,0,1,1,0,NULL),(68,'email_bcc','The BCC field specifies the email addresses of any recipients that were included in the blind carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,NULL),(69,'email_cc','The CC field specifies the email addresses of any recipients that were included in the carbon copy header of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,NULL),(70,'email_content_type','The Content-Type field specifies the internet media, or MIME, type of the email message content.','^.+$',1,0,1,1,0,NULL),(71,'email_errors_to','The Errors_To field specifies the entry in the (deprecated) errors_to header of the email message.','^.+$',1,0,1,1,0,NULL),(72,'email_from','The From field specifies the email address of the sender of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,1,'9cfa1e1b74a725ac80fd0dfb152c69795b956540'),(73,'email_in_reply_to','The In_Reply_To field specifies the message ID of the message that this email is a reply to.','^.+$',1,0,1,1,0,NULL),(74,'email_message_id','The Message_ID field specifies the automatically generated ID of the email message.','^.+$',1,0,1,1,0,NULL),(75,'email_mime_version','The MIME-Version field specifies the version of the MIME formatting used in the email message.','^.+$',1,0,1,1,0,NULL),(76,'email_raw_body','The Raw_Body field specifies the complete (raw) body of the email message.','^.+$',1,6,1,0,0,NULL),(77,'email_raw_header','The Raw_Header field specifies the complete (raw) headers of the email message.','^.+$',0,0,1,0,0,'daf734a6e8be0d50df78677781de72f028b8c46a'),(78,'email_receive_datetime','The Date field specifies the date/time that the email message was received by the mail server.','^.+$',2,7,1,1,0,NULL),(79,'email_relay_ip','This attribute hold the IP address of an MTA used to deliver the mail.','^.+$',1,0,1,1,1,'53d2d3d8710d87f30e0dbf9c9e3402e5591d9c4b'),(80,'email_reply_to','The Reply_To field specifies the email address that should be used when replying to the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,0,NULL),(81,'email_send_datetime','The Date field specifies the date/time that the email message was sent.','^.+$',2,7,1,1,0,NULL),(82,'email_sender','The Sender field specifies the email address of the sender who is acting on behalf of the author listed in the From: field','^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,0,1,1,0,NULL),(83,'email_server','The Email_Server field is optional and specifies the relevant email server.','^.+$',1,0,1,1,0,NULL),(84,'email_subject','The Subject field specifies the subject (a brief summary of the message topic) of the email message.','^.+$',1,0,1,1,0,NULL),(85,'email_to','The To field specifies the email addresses of the recipients of the email message.','^[A-Za-z0-9._%+-]+@(?:[A-Za-
z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,NULL),(86,'email_x_mailer','The X-Mailer field specifies the software used to send the email message. This field is non-standard.','^.+$',1,0,1,1,0,NULL),(87,'email_x_originating_ip','The X-Originating-IP field specifies the originating IP Address of the email sender, in terms of their connection to the mail server used to send the email message. This field is non-standard.','^.+$',1,0,1,1,0,NULL),(88,'code_language','The code_language field refers to the code language used in the code characterized in this field.','^.+$',1,0,1,1,0,NULL),(89,'processor_family','The processor_family field specifies the class of processor that the code snippet is targeting. Possible values: x86-32, x86-64, IA-64, PowerPC, ARM, Alpha, SPARC, z/Architecture, eSi-RISC, MIPS, Motorola 68k, Other.','^.+$',1,0,1,1,0,NULL),(90,'targeted_platform','The Targeted_Platforms field specifies a list platforms that this code is targeted for.','^.+$',1,0,1,1,0,NULL),(91,'antivirus_record','The results of one or many antivirus scans for an object. This is a multiline csv value (datetime, engine, result, threat name).','^.+$',1,5,1,1,0,NULL),(92,'ida_pro_file','An IDA pro file.','^.+$',1,6,1,1,0,NULL),(93,'log_records','Free text for storing log information.','^.+$',0,0,1,1,0,NULL),(94,'whois','Whois network information','^.+$',0,0,1,1,0,NULL),(95,'asn','The asn value specifies an identifier for an autonomous system number.','^.+$',1,0,1,1,1,'c4b7ba59f89604d79e518bf8b48fe434ff8b20c7'),(96,'domain','Contains a fully qualified domain name','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,0,NULL),(97,'file_content_pattern','Contains a pattern that can be found in the raw file data','^.+$',1,0,1,1,0,NULL),(98,'file_full_path_pattern','A pattern that matches the full path of a file','^.+$',1,0,1,1,0,NULL),(99,'file_name_pattern','A pattern that matches the file name','^.+$',1,0,1,1,0,NULL),(100,'hostname_c&c','Fully qualified domain name of a host hosting a command and control server','^(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,4}$',1,5,1,1,1,'3030c45848fa71ebe5a658ba69ebe9c80eb51fa7'),(101,'ids_rules','Holds IDS rules. These rules need to be prefixed with the used format (e.g. snort).','^.+$',0,0,1,1,0,NULL),(102,'ipv4_addr','The IPv4-addr value specifies an IPV4 address.','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,5,1,1,0,NULL),(103,'ipv4_addr_c&c','IPv4 address hosting a command and control server','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$',1,5,1,1,1,'bc0a065aa9458c8332517e678dc2cf11d2e47ab7'),(104,'ipv4_net','IPv4 CIDR block','^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}/\\d{1,2}$',1,5,1,1,0,NULL),(105,'ipv6_addr','The IPv6-addr value specifies an IPv6 address.','^.+$',1,5,1,1,0,NULL),(106,'ipv6_addr_c&c','IPv6 address hosting a command and control server','^.+$',1,5,1,1,1,'1788e4f3bf6fd6a2b4ccd1e1761d851d3a8b5721'),(107,'ipv6_net','IPv6 sub-network','^.+$',1,5,1,1,0,NULL),(108,'mutex','The Mutex object is intended to characterize generic mutual exclusion (mutex) objects.','^.+$',1,0,1,1,0,NULL),(109,'open_ioc_definition','Hold open IOC definitions.','^.+$',1,6,1,1,0,'0cad1a806dfecd8b78659fb1d859cc40de1968af'),(110,'trafic_content_pattern','Pattern matching network traffic content.','^.+$',1,0,1,1,0,NULL),(111,'url','Holds a complete URL (e.g. http://www.govcert.lu/en/index.hmtl)','^.+$',1,5,1,1,0,NULL),(112,'url_path','Holds only the path part of an URL. (e.g. /en/index.html)','^.+$',1,5,1,1,0,NULL),(113,'url_pattern','Holds a pattern that matches URL.','^.+$',1,5,1,1,0,NULL),(114,'win_registry_key','The WindowsRegistryObjectType type is intended to characterize Windows registry objects, including Keys and Key/Value pairs.','^.+$',0,0,1,1,1,'2d110b2d1019751b7e09ed5831320364b88626de'),(115,'yara_rule','Holds YARA rules used to identify and classify malware samples.','^.+$',0,0,1,1,1,'cdb3d8e146f88e7ab652207429afa5458da55dd1');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DEF_Objects`
--

LOCK TABLES `DEF_Objects` WRITE;
/*!40000 ALTER TABLE `DEF_Objects` DISABLE KEYS */;
INSERT INTO `DEF_Objects` (`def_object_id`, `name`, `description`, `chksum`, `sharable`) VALUES (1,'generic_file','Generic file','7a6272431a4546b99081d50797201ddc25a38f4c',1),(2,'reference_document','reference_document','dee32f113d56844d27b15c236d7fb66afdbef085',1),(3,'references','references','f4c9a69f715c3c60aa2fc15795b3834d2dc51b9d',1),(4,'network_traffic','network_traffic','468bc69e746c453763f1c1ed644742628ca4bb38',1),(5,'email','email','a88b7dcd1a9e3e17770bbaa6d7515b31a2d7e85d',1),(6,'executable_file','executable_file','f82c52727e0d45c79cd3810704314d6c08fed47a',1),(7,'forensic_records','forensic_records','fc771f573182da23515be31230903ec2c45e8a3a',1),(8,'ioc_records','ioc_records','4ffb865c9d6950a643fd29d7170e849b1d077b9a',1),(9,'malicious_website','malicious_website','e34bafaf6afd4a30188913d181fce87d85fcf037',1),(10,'source_code','source_code','0c4fa34ab948d93a78795a5301c11f772a635620',1);
/*!40000 ALTER TABLE `DEF_Objects` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `DObj_has_DAttr`
--

LOCK TABLES `DObj_has_DAttr` WRITE;
/*!40000 ALTER TABLE `DObj_has_DAttr` DISABLE KEYS */;
INSERT INTO `DObj_has_DAttr` (`def_object_id`, `def_attribute_id`) VALUES (1,29),(5,29),(6,29),(10,29),(1,30),(5,30),(6,30),(10,30),(1,31),(5,31),(6,31),(10,31),(1,32),(5,32),(6,32),(10,32),(1,33),(5,33),(6,33),(10,33),(1,34),(6,34),(10,34),(1,35),(6,35),(8,35),(10,35),(1,36),(6,36),(10,36),(1,37),(6,37),(10,37),(3,38),(1,39),(5,39),(6,39),(9,39),(10,39),(1,40),(6,40),(10,40),(2,41),(8,42),(1,43),(2,43),(3,43),(4,43),(6,43),(7,43),(8,43),(9,43),(10,43),(1,44),(2,44),(3,44),(4,44),(6,44),(7,44),(8,44),(9,44),(10,44),(1,45),(5,45),(6,45),(10,45),(1,46),(6,46),(10,46),(1,47),(6,47),(8,47),(10,47),(1,48),(6,48),(10,48),(1,49),(6,49),(10,49),(1,50),(6,50),(8,50),(10,50),(1,51),(6,51),(10,51),(1,52),(6,52),(10,52),(1,53),(6,53),(10,53),(1,54),(6,54),(10,54),(1,55),(6,55),(10,55),(1,56),(6,56),(10,56),(1,57),(4,57),(6,57),(10,57),(1,58),(5,58),(6,58),(9,58),(10,58),(1,59),(2,59),(3,59),(4,59),(5,59),(6,59),(7,59),(8,59),(9,59),(10,59),(1,60),(2,60),(3,60),(4,60),(5,60),(6,60),(7,60),(8,60),(9,60),(10,60),(1,61),(4,61),(5,61),(6,61),(7,61),(9,61),(10,61),(2,62),(3,63),(3,64),(4,65),(4,66),(5,67),(5,68),(5,69),(5,70),(5,71),(5,72),(5,73),(5,74),(5,75),(5,76),(5,77),(5,78),(5,79),(5,80),(5,81),(5,82),(5,83),(5,84),(5,85),(5,86),(5,87),(6,88),(10,88),(6,89),(10,89),(6,90),(10,90),(7,91),(7,92),(7,93),(7,94),(9,94),(8,95),(8,96),(8,97),(8,98),(8,99),(8,100),(8,101),(8,102),(9,102),(8,103),(8,104),(8,105),(9,105),(8,106),(8,107),(8,108),(8,109),(8,110),(8,111),(9,111),(8,112),(8,113),(8,114),(8,115);
/*!40000 ALTER TABLE `DObj_has_DAttr` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `DateValues`
--

LOCK TABLES `DateValues` WRITE;
/*!40000 ALTER TABLE `DateValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `DateValues` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Events`
--

LOCK TABLES `Events` WRITE;
/*!40000 ALTER TABLE `Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `Events` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Events_has_Objects`
--

LOCK TABLES `Events_has_Objects` WRITE;
/*!40000 ALTER TABLE `Events_has_Objects` DISABLE KEYS */;
/*!40000 ALTER TABLE `Events_has_Objects` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Groups`
--

LOCK TABLES `Groups` WRITE;
/*!40000 ALTER TABLE `Groups` DISABLE KEYS */;
INSERT INTO `Groups` (`group_id`, `name`, `description`, `canDownlad`, `tlplvl`, `email`, `usermails`, `pgpKey`) VALUES (1,'Default_Group','Default Group, for all users',0,3,'a@a.com',0,NULL),(2,'GOVCERT.LU','GOVCERT.LU',1,0,'ops@govcert.etat.lu',1,NULL);
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
-- Dumping data for table `Groups_has_Events`
--

LOCK TABLES `Groups_has_Events` WRITE;
/*!40000 ALTER TABLE `Groups_has_Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `Groups_has_Events` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `NumberValues`
--

LOCK TABLES `NumberValues` WRITE;
/*!40000 ALTER TABLE `NumberValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `NumberValues` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Obj_links_Obj`
--

LOCK TABLES `Obj_links_Obj` WRITE;
/*!40000 ALTER TABLE `Obj_links_Obj` DISABLE KEYS */;
/*!40000 ALTER TABLE `Obj_links_Obj` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Objects`
--

LOCK TABLES `Objects` WRITE;
/*!40000 ALTER TABLE `Objects` DISABLE KEYS */;
/*!40000 ALTER TABLE `Objects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `StringValues`
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
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `StringValues`
--

LOCK TABLES `StringValues` WRITE;
/*!40000 ALTER TABLE `StringValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `StringValues` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `SubGroups_has_Events`
--

LOCK TABLES `SubGroups_has_Events` WRITE;
/*!40000 ALTER TABLE `SubGroups_has_Events` DISABLE KEYS */;
/*!40000 ALTER TABLE `SubGroups_has_Events` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Subgroups`
--

LOCK TABLES `Subgroups` WRITE;
/*!40000 ALTER TABLE `Subgroups` DISABLE KEYS */;
/*!40000 ALTER TABLE `Subgroups` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Subgroups_has_Groups`
--

LOCK TABLES `Subgroups_has_Groups` WRITE;
/*!40000 ALTER TABLE `Subgroups_has_Groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `Subgroups_has_Groups` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `TextValues`
--

LOCK TABLES `TextValues` WRITE;
/*!40000 ALTER TABLE `TextValues` DISABLE KEYS */;
/*!40000 ALTER TABLE `TextValues` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` (`user_id`, `username`, `password`, `privileged`, `last_login`, `email`, `disabled`, `apikey`, `group_id`, `pgpKey`) VALUES (1,'admin','dd94709528bb1c83d08f3088d4043f4742891f4f',1,'2013-11-26 12:11:59','admin@admin.com',0,NULL,1,NULL),(2,'georges','EXTERNALAUTH',1,'2013-11-22 18:37:21','georges.toth@govcert.etat.lu',0,NULL,2,NULL),(3,'patrick','EXTERNALAUTH',1,NULL,'patrick.houtsch@govcert.etat.lu',0,NULL,2,NULL),(4,'michele','EXTERNALAUTH',0,NULL,'michele.ludivig@govcert.etat.lu',0,NULL,2,NULL),(5,'guy','EXTERNALAUTH',1,NULL,'guy.foetz@govcert.etat.lu',0,NULL,2,NULL),(6,'jhemp','EXTERNALAUTH',1,NULL,'jean-paul.weber@govcert.etat.lu',0,NULL,2,NULL);
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

-- Dump completed on 2013-11-26 13:24:55
