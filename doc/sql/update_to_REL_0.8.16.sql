update Objects set parentEvent = event_id where parentEvent is Null;
ALTER TABLE Objects DROP FOREIGN KEY `FK_objects_events_event_id` ;
ALTER TABLE Objects DROP COLUMN `event_id`, DROP INDEX `IDX_objects_events_event_id` ;
