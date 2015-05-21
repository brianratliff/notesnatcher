-- Note Snatcher:  a simple notes organizer
-- Copyright (C) 2015 Brian Ratliff
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.

CREATE TABLE [notebook] (
    key TEXT,
    val TEXT);
--------------------------------------------------
CREATE TABLE [notes] (
    id INTEGER PRIMARY KEY NOT NULL,
    notetype INTEGER,
    crtime DATETIME DEFAULT current_timestamp,
    mtime DATETIME DEFAULT current_timestamp,
    subject TEXT,
    url TEXT,
    notedata TEXT);
--------------------------------------------------
CREATE TRIGGER [update_edit]
    BEFORE UPDATE OF [notedata]
    ON [notes]
    BEGIN
        UPDATE notes
        SET mtime = current_timestamp
        WHERE id = NEW.id;
    END;
--------------------------------------------------
CREATE TRIGGER [delete_relationships]
    BEFORE DELETE
    ON [notes]
    BEGIN
        DELETE FROM notes_tags
        WHERE note = OLD.id;
    END;
--------------------------------------------------
--------------------------------------------------
CREATE TABLE [tags] (
    [id] INTEGER NOT NULL PRIMARY KEY,
    [name] TEXT,
    [count] INT NOT NULL ON CONFLICT REPLACE DEFAULT 0);
--------------------------------------------------
CREATE TABLE [notes_tags] (
    note INTEGER NOT NULL,
    tag INTEGER NOT NULL,
    CONSTRAINT [No_Dupes]
        UNIQUE([note], [tag])
        ON CONFLICT IGNORE);
--------------------------------------------------
CREATE TRIGGER [purge_unused_tags]
    AFTER DELETE
    ON [notes_tags]
    BEGIN
        DELETE FROM tags
        WHERE count < 1;
    END;
--------------------------------------------------
--------------------------------------------------
CREATE TRIGGER [decrement_tags_count]
    AFTER DELETE
    ON [notes_tags]
    BEGIN
        UPDATE tags
        SET count = (count - 1)
        WHERE tags.id = OLD.tag;
    END;
--------------------------------------------------
CREATE TRIGGER [increment_tags_count]
    AFTER INSERT
    ON [notes_tags]
    BEGIN UPDATE tags
        SET count = (count + 1)
        WHERE tags.id = NEW.tag;
    END;
--------------------------------------------------
--------------------------------------------------
CREATE VIEW [subject_by_creation]
    AS SELECT subject, datetime(crtime, 'localtime')
    FROM notes ORDER BY crtime;
--------------------------------------------------
CREATE VIEW [subject_by_edit]
    AS SELECT subject, datetime(mtime, 'localtime')
    FROM notes ORDER BY mtime;
--------------------------------------------------
CREATE VIEW [subjects_and_tags]
    AS SELECT notes.subject AS 'Subject', tags.name AS 'Tag'
    FROM notes_tags
    INNER JOIN notes
    ON notes.id = notes_tags.note
    INNER JOIN tags
    ON tags.id = notes_tags.tag;
--------------------------------------------------
--------------------------------------------------
CREATE TABLE [trash] (
    id INTEGER PRIMARY KEY NOT NULL,
    crtime DATETIME DEFAULT current_timestamp,
    mtime DATETIME DEFAULT current_timestamp,
    deltime DATETIME DEFAULT current_timestamp,
    subject TEXT,
    tags TEXT,
    url TEXT,
    notedata TEXT);
--------------------------------------------------
CREATE TRIGGER [move_to_trash]
    BEFORE DELETE ON [notes]
    BEGIN
        INSERT INTO trash (crtime, mtime, subject, url, notedata, tags)
        VALUES (OLD.crtime, OLD.mtime, OLD.subject, OLD.url, OLD.notedata, (
            SELECT group_concat(tags.name, ' ')
            FROM tags INNER JOIN (
                SELECT tag FROM notes_tags
                WHERE notes_tags.note = OLD.id) AS tag_ids
            ON tags.id = tag_ids.tag));
    END;
--------------------------------------------------
CREATE TABLE [temp_notes] (
    id INTEGER PRIMARY KEY NOT NULL,
    noteid INTEGER DEFAULT -1,
    subject TEXT,
    tags TEXT,
    url TEXT,
    notedata TEXT,
    CONSTRAINT [Single_Autosave] UNIQUE([noteid]) ON CONFLICT REPLACE);
