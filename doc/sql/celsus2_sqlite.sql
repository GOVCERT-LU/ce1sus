CREATE TABLE `Attributes` (
  `attribute_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `def_attribute_id` INT NOT NULL ,
  `user_id` INT NOT NULL ,
  `object_id` INT(11) NOT NULL ,
  
  CONSTRAINT `FK_Attr_DAttr_attribute_id`
    FOREIGN KEY (`def_attribute_id` )
    REFERENCES`DEF_Attributes` (`def_attribute_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_Attr_Users_user_id`
    FOREIGN KEY (`user_id` )
    REFERENCES`Users` (`user_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_Attr_Objects_object_id`
    FOREIGN KEY (`object_id` )
    REFERENCES`objects` (`object_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Comments` (
  `comment_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `event_id` integer NOT NULL ,
  `user_id` integer NOT NULL ,
  `comment` TEXT NULL DEFAULT NULL ,
  `created` DATETIME NULL DEFAULT NULL ,
  CONSTRAINT `FK_events_comments_event_id`
    FOREIGN KEY (`event_id` )
    REFERENCES`Events` (`event_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_user_comments_user_id`
    FOREIGN KEY (`user_id` )
    REFERENCES`Users` (`user_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `DEF_Attributes` (
  `def_attribute_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `name` VARCHAR(45) NOT NULL ,
  `description` VARCHAR(255) NULL DEFAULT 'N/A' ,
  `regex` VARCHAR(255) NULL DEFAULT '.*' ,
  `valuetable` INT(1) NULL DEFAULT '0' );
CREATE TABLE `DEF_Objects` (
  `def_object_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `name` VARCHAR(45) NOT NULL ,
  `description` VARCHAR(255) NULL DEFAULT NULL 
  );
CREATE TABLE `DObj_has_DAttr` (
  `def_object_id` INT NOT NULL ,
  `def_attribute_id` INT NOT NULL ,
  
  CONSTRAINT `FK_DObjs_DAttrs_DOId`
    FOREIGN KEY (`def_object_id` )
    REFERENCES`DEF_Objects` (`def_object_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_DAttrs_DObjs_DAttrID`
    FOREIGN KEY (`def_attribute_id` )
    REFERENCES`DEF_Attributes` (`def_attribute_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE);
CREATE TABLE `DateValues` (
  `DateValue_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `value` DATETIME NULL DEFAULT NULL ,
  `attribute_id` INT NOT NULL ,
  
  CONSTRAINT `FK_DateValues_Attr_attribute_id`
    FOREIGN KEY (`attribute_id` )
    REFERENCES`Attributes` (`attribute_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Event_has_Tickets` (
  `event_id` INT NOT NULL ,
  `ticket_id` INT NOT NULL ,
  
  CONSTRAINT `FK_event_ticket_event_id`
    FOREIGN KEY (`event_id` )
    REFERENCES`Events` (`event_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_ticket_event_ticket_id`
    FOREIGN KEY (`ticket_id` )
    REFERENCES`Tickets` (`user_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Event_links_Event` (
  `event_id_from` INT NOT NULL ,
  `event_id_to` INT NOT NULL ,
  
  CONSTRAINT `fk_ElE_Events_from`
    FOREIGN KEY (`event_id_from` )
    REFERENCES`Events` (`event_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_ElE_Events_to`
    FOREIGN KEY (`event_id_to` )
    REFERENCES`Events` (`event_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Events` (
  `event_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `description` TEXT NULL DEFAULT NULL ,
  `short_description` VARCHAR(255) NULL DEFAULT NULL ,
  `created` DATETIME NULL DEFAULT NULL ,
  `first_seen` DATETIME NULL DEFAULT NULL ,
  `last_seen` DATETIME NULL DEFAULT NULL ,
  `modified` DATETIME NULL DEFAULT NULL ,
  `published` TINYINT(1) NULL DEFAULT '0' ,
  `stauts` INT(11) NULL DEFAULT '0' ,
  `tlp_level` INT(1) NULL DEFAULT '3' ,
  `user_id` INT NOT NULL ,
  
  CONSTRAINT `fk_Events_users_user_id`
    FOREIGN KEY (`user_id` )
    REFERENCES`Users` (`user_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Events_has_Objects` (
  `event_id` INT NOT NULL ,
  `object_id` INT NOT NULL ,
  
  CONSTRAINT `FK_Events_Objects_event_id`
    FOREIGN KEY (`event_id` )
    REFERENCES`Events` (`event_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_Objects_Event_object_id`
    FOREIGN KEY (`object_id` )
    REFERENCES`objects` (`object_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Events_has_Tickets` (
  `event_id` INT NOT NULL ,
  `ticked_id` INT NOT NULL ,
  PRIMARY KEY (`event_id`, `ticked_id`) ,
  CONSTRAINT `FK_Events_Tickets_event_id`
    FOREIGN KEY (`event_id` )
    REFERENCES`Events` (`event_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_Tickets_Events_ticket_id`
    FOREIGN KEY (`ticked_id` )
    REFERENCES`Tickets` (`ticked_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE);
CREATE TABLE `Groups` (
  `group_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `name` VARCHAR(45) NULL DEFAULT NULL ,
  `auto_share_tlp` INT(1) NULL DEFAULT NULL );
CREATE TABLE `Groups_has_Events` (
  `group_id` INT(11) NOT NULL ,
  `event_id` INT NOT NULL ,
  
  CONSTRAINT `FK_Groups_Events_Group_id`
    FOREIGN KEY (`group_id` )
    REFERENCES`Groups` (`group_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_Events_Groups_event_id`
    FOREIGN KEY (`event_id` )
    REFERENCES`Events` (`event_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `NumberValue` (
  `NumberValue_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `value` DECIMAL(10,0) NULL DEFAULT NULL ,
  `attribute_id` INT NOT NULL ,
  
  CONSTRAINT `fk_NumberValues_attr_attribute_id`
    FOREIGN KEY (`attribute_id` )
    REFERENCES`Attributes` (`attribute_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Obj_links_Obj` (
  `object_id_to` INT NOT NULL ,
  `Objects_id_from` INT NOT NULL ,
  
  CONSTRAINT `FK_Olo_Obj_object_id`
    FOREIGN KEY (`object_id_to` )
    REFERENCES`Objects` (`object_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `FK_OlO_Obj_object_id`
    FOREIGN KEY (`Objects_id_from` )
    REFERENCES`Objects` (`object_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE);
CREATE TABLE `Objects` (
  `object_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `user_id` INT NOT NULL ,
  `tlp_level` INT(1) NULL DEFAULT NULL ,
  `def_object_id` INT NOT NULL ,
  
  CONSTRAINT `FK_DObj_objects_def_object_id`
    FOREIGN KEY (`def_object_id` )
    REFERENCES`DEF_Objects` (`def_object_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_users_objects_user_id`
    FOREIGN KEY (`user_id` )
    REFERENCES`Users` (`user_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `StringValues` (
  `StringValue_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `value` VARCHAR(255) NULL DEFAULT NULL ,
  `attribute_id` INT NOT NULL ,
  
  CONSTRAINT `fk_StringValues_attr_attribute_id`
    FOREIGN KEY (`attribute_id` )
    REFERENCES`Attributes` (`attribute_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `TextValues` (
  `TextValue_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `value` TEXT NULL DEFAULT NULL ,
  `attribute_id` INT NOT NULL ,
  
  CONSTRAINT `FK_TextValues_attr_attribute_id`
    FOREIGN KEY (`attribute_id` )
    REFERENCES`Attributes` (`attribute_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `Tickets` (
  `ticked_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `user_id` INT NOT NULL ,
  `ticket` VARCHAR(45) NULL DEFAULT NULL ,
  `created` DATETIME NULL DEFAULT NULL ,
  
  CONSTRAINT `fk_tickets_users_user_id`
    FOREIGN KEY (`user_id` )
    REFERENCES`Users` (`user_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
CREATE TABLE `User_has_Groups` (
  `user_id` INT NOT NULL ,
  `group_id` INT(11) NOT NULL ,
  
  CONSTRAINT `fk_users_groups_group_id`
    FOREIGN KEY (`group_id` )
    REFERENCES`Groups` (`group_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_users_groups_user_id`
    FOREIGN KEY (`user_id` )
    REFERENCES`Users` (`user_id` )
    ON DELETE CASCADE
    ON UPDATE CASCADE);
CREATE TABLE `Users` (
  `user_id` INTEGER  primary key AUTOINCREMENT NOT NULL  ,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL ,
  `privileged` INTeger DEFAULT NULL ,
  `last_login` DATETIME  DEFAULT NULL ,
  `email` VARCHAR(45) DEFAULT NULL 
  );
CREATE INDEX `IDX_EhT_event_id` ON`Events_has_Tickets` (`event_id` ASC);
CREATE INDEX `IDX_EhT_ticket_id` ON`Events_has_Tickets` (`ticked_id` ASC);
CREATE UNIQUE INDEX `user_id_UNIQUE` ON`Users` (`user_id` ASC);
