#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       snatcher.py
#
#       The Snatcher note and notes database stuff
"""
Note Snatcher:  a simple notes organizer
Copyright (C) 2015 Brian Ratliff

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import os
import random
import sqlite3
import sys
import time
#import xml.sax
#import xml.sax.handler  #flakes whining:  TODO

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class note():
    def __init__(self, noteid=-1, subject="", tags=set(), tagstring="",
            oldtags=[], url="", notedata="", crtime="", mtime="", deltime=""):
        self.noteid = noteid
        self.subject = subject
        self.tags = set(tags)
        self.tagstring = tagstring
        self.oldtags = oldtags
        self.url = url
        self.notedata = notedata
        self.crtime = crtime
        self.mtime = mtime
        self.deltime = deltime

    def __str__(self):
        return unicode("ID: %d\nCreated: %s\nEdited: %s\n"
            "Subject: %s\nURL: %s\nTags: %s\nNotedata: %s\n"
            % (self.noteid, self.crtime, self.mtime, self.subject,
            self.url, self.get_tags_string(), self.notedata[:79]))

    def get_tags_string(self):
        """Get all tags as one string."""
        taglist = sorted(list(self.tags))
        return " ".join(taglist)


class notebook():
    def __init__(self, filename="new_notebook.db", create=False):
        """Create a new notebook database object.

        notebook(filename="new_notebook.db", create=False)

        Pass the path and file name to the SQLite 3 Snatcher database.
        create specifies whether or not to create the notebook.
        """
        self.db = ""
        self.currentNote = note()
        self.tags = set()

        # check for existence of file and add it if it exists to self.db
        # This should probably break down the file argument into a path and
        # file name component and check for the existence of both.
        if os.path.exists(filename) and not create:
            logger.info("Path exists for file: %s" % filename)
            self.db = filename
            return
        elif not create:
            # If the [default] database doesn't exist, create it.
            logger.info("Passed path (%s) does not exist." % filename)
            # Change default db file to home dir if in linux:
            # ~/.snatcher/notes.db.
            if sys.platform == 'linux2' or sys.platform == 'darwin':
                self.db = os.environ["HOME"] + \
                    "/.snatcher/new_notebook.db"
                #print("self.db = %s" % self.db)
                new_path = os.path.join(os.environ["HOME"], ".snatcher")
                if not os.path.exists(new_path):
                    os.mkdir(new_path)
                    logger.info("using Linux, path = %s" % new_path)
            elif sys.platform == 'win32':
                # If it's Windows, put notes db in My Documents.
                self.db = os.environ["USERPROFILE"] + "\\new_notebook.db"
                logger.info("using Windows, path = %s" % self.db)
            else:
                # TODO
                # Otherwise, just print the platform and deal with this later.
                logger.info("platform is %s" % sys.platform)
            # Now check for the default notes db.
            if os.path.exists(self.db):
                logger.info("Default notes db exists.")
                # great, return
                return
            else:
                self.create_database(self.db)
                return
        elif create:
            logger.info("About to create new DB with path: %s" % filename)
            # Now try to create the notes database.
            # TODO
            # This should probably throw an exception if there is a problem.
            self.db = filename
            self.create_database(self.db)
        logger.info("DB should exist, path: %s\nself.db = %s" % (filename,
            self.db))

    def create_database(self, dbname="mynotes.db"):
        """Create a new notebook database.

        create_database(dbname="mynotes.db")
        Create a new notebook database with specified name.
        """

        try:
            con = sqlite3.connect(dbname)
            cur = con.cursor()
            with open("snatcher.sql", "r") as snatchersql:
                all_lines = snatchersql.readlines()
                sql = "".join(all_lines)
            cur.executescript(sql)
            con.commit()
            con.close()
        except Exception as exc:
            logger.info("Exception (CreateDB): %s" % exc)
            logger.exception(exc)
            return -1

    def import_notes(self, filename, fileformat="xml", use_localtime=False):
        """Import notes from the specified file.

        import_notes(filename, fileformat="xml", use_localtime=False)
        use_localtime specifies whether or not to treat imported dates as being in localtime
        """
        imported_notes = set()
        count = 1
        import xml.etree.cElementTree as etree
        tree = etree.parse(filename)
        root = tree.getroot()
        for i in root:
            n = note()
            try:
                if i.get("subject"):
                    n.subject = i.get("subject")
                if i.get("url"):
                    n.url = i.get("url")
                if i.get("tags"):
                    n.tags = i.get("tags")
                if i.get("crtime"):
                    n.crtime = i.get("crtime")
                if i.get("mtime"):
                    n.mtime = i.get("mtime")
                if i.text:
                    n.notedata = i.text
            except Exception as ex:
                logger.exception(ex)
            imported_notes.add(n)
            count += 1

        con = sqlite3.connect(self.db)
        cur = con.cursor()

        logger.info("starting loop to insert into db")

        for n in imported_notes:
            if use_localtime:
                q = "INSERT INTO notes " \
                    "(subject, datetime(crtime, 'localtime'), " \
                    "datetime(mtime, 'localtime'), notedata, url) " \
                    "VALUES (?, ?, ?, ?, ?);"
            else:
                q = "INSERT INTO notes (subject, crtime, mtime, " \
                   "notedata, url) VALUES (?, ?, ?, ?, ?);"
            args = (n.subject, n.crtime, n.mtime, n.notedata, n.url)
            cur.execute(q, args)
            #con.commit()

            nid = cur.lastrowid

            # add the tags using new and improved add_note_tags method
            if n.tags:
                con.commit()
                logger.info("Tags: %s" % n.tags)
                self.add_note_tags(nid, n.tags.split(" "))

            # now do the tags
            #self.select_new_note()
            #self.update_tags(n.tagstring)
        con.commit()
        cur.close()
        con.close()
        logger.info("import done.")

    def export_notes(self, filename, fileformat="xml", use_localtime=False):
        """ Export notes to XML file.

        export_notes(filename, fileformat="xml", use_localtime=False)

        The different mode types are:
        xml is Snatcher XML which is UTF-8 with Unix-style line endings.
        html is HTML as UTF-8 and Unix-style line endings.

        use
        use_localtime specifies whether or not to treat exported dates as being in localtime
        """
        import codecs
        # get all notes
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        if use_localtime:
            q = "SELECT id, subject, datetime(crtime, 'localtime'), " \
                "datetime(mtime, 'localtime'), notedata, url FROM notes " \
                "ORDER BY crtime;"
        else:
            q = "SELECT id, subject, crtime, mtime, notedata, url " \
                "FROM notes ORDER BY crtime;"
        cur.execute(q)
        results = cur.fetchall()
        allnotes = []
        for i in results:
            n = note()
            n.noteid = i[0]
            n.subject = i[1]
            n.subject = codecs.encode(i[1], 'ascii', 'xmlcharrefreplace')
            #n.subject = enc(i[i], 'xmlcharrefreplace')[0]
            # if there are any reserved characters, replace them
            # http://www.w3schools.com/tags/ref_entities.asp
            reserved = ("&", "'", '"', "<", ">")
            for r in reserved:
                if r in n.subject:
                    newchar = "&#%d;" % ord(r)
                    n.subject = n.subject.replace(r, newchar)
                    logger.info("r = %s\tnewchar = %s" % (r, newchar))
            n.crtime = i[2]
            n.mtime = i[3]
            n.notedata = i[4]
            n.url = i[5]
            # if i write the characters properly, it won't import back in right
            #n.notedata = codecs.encode(i[4], 'ascii', 'xmlcharrefreplace')
            # now get tags
            q = "SELECT tags.name FROM tags INNER JOIN " \
                "(SELECT tag FROM notes_tags WHERE notes_tags.note = %d) " \
                "AS tag_ids ON tags.id = tag_ids.tag" % n.noteid
            cur.execute(q)
            results = cur.fetchall()
            for i in results:
                n.tags.add(i[0])
            allnotes.append(n)

        try:
            if fileformat == "xml":
                # snatcher xml
                file = codecs.open(filename, "w", encoding="utf8")
            elif fileformat == "html":
                # html
                file = codecs.open(filename, "w", encoding="utf8")
            elif fileformat == "txt":
                # UTF-8 text
                file = codecs.open(filename, "w", encoding="utf8")
            else:
                logger.info("Unknown type: %s" % type)
                return

            logger.info(file.name)
        except Exception as exc:
            logger.info("Problem opening the file: " + filename)
            logger.exception(exc)
            return
        # write leading file stuff
        if fileformat == "xml":
            filehead = '<?xml version="1.0" encoding="utf-8"?>\n<notebook>\n'
            file.write(filehead)
        elif fileformat == "html":
            filehead = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 ' \
                'Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-' \
                'transitional.dtd">\n<html>\n<head>\n<title>Snatcher Notes' \
                '</title>\n<meta http-equiv="Content-Style-Type" ' \
                'content="text/css" />\n<meta http-equiv="Content-Type" ' \
                'content="text/html; charset=utf-8" />\n</head>\n<body>\n\n'
            file.write(filehead)
        elif fileformat == "txt":
            pass
            filehead = "Snatcher Notes exported notes\n[%s]\n" % self.db
            file.write(filehead)

        for n in allnotes:
            thisnote = "<note "
            if fileformat == "xml":
                thisnote += 'subject="%s" ' % n.subject
                thisnote += 'url="%s" ' % n.url
                thisnote += 'crtime="%s" ' % n.crtime
                thisnote += 'mtime="%s" ' % n.mtime
                thisnote += 'tags="%s">' % n.get_tags_string()
                thisnote += "<![CDATA[%s]]></note>\n" % n.notedata
                file.write(thisnote)
            elif fileformat == "html":
                thisnote = '<h3><u><a href="%s">%s</a></u></h3>\n' % (n.url,
                    n.subject)
                thisnote += "<p>Created: %s<br/>\n" % n.crtime
                thisnote += "Last mtime: %s<br/>\n" % n.mtime
                thisnote += "Tags: %s</p>\n" % n.get_tags_string()
                thisnote += "<p>%s</p>\n" % n.notedata.replace("\n", "<br/>")
                thisnote += "<hr/>\n\n"
                file.write(thisnote)
            elif fileformat == "txt":
                thisnote = "-" * 50 + '\n'
                thisnote += "Subject: %s\n" % n.subject
                thisnote += "URL: %s\n" % n.url
                thisnote += "Created: %s\n" % n.crtime
                thisnote += "Edited: %s\n" % n.mtime
                thisnote += "Tags: %s\n" % n.get_tags_string()
                thisnote += "%s\n" % n.notedata
                file.write(thisnote)
        # write ending
        ending = "</notebook>"
        if fileformat == "xml":
            file.write(ending)
        elif fileformat == "html":
            ending = "</body>\n</html>\n"
            file.write(ending)
        file.close()
        logger.info("File saved.\n")
        return

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

    def count(self):
        """ Get the count of all notes """
        try:
            con = sqlite3.connect(self.db)
            cur = con.cursor()
            q = "SELECT COUNT(*) FROM notes;"
            cur.execute(q)
            r = cur.fetchone()
            count = int(r[0])
            cur.close()
            con.close()
            return count
        except Exception as exc:
            logger.info("EXCEPTION (Count()): %s" % exc)
            logger.exception(exc)
            return -1

    def add_note(self, n):
        """ Insert a new note into the database

        add_note(n) -> id

        Return id of note.
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "INSERT INTO notes (subject, url, notedata) VALUES (?, ?, ?);"
        args = (n.subject, n.url, n.notedata)
        cur.execute(q, args)
        newid = cur.lastrowid
        con.commit()
        cur.close()
        con.close()
        return newid

    def add_temp_note(self, n):
        """ Insert a temporary note into the database.

        add_temp_note(n)
        """
        print("inside add_temp_note()")
        print "About to add temp note:"
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "INSERT INTO temp_notes (noteid, subject, notedata, tags, url) " \
            "VALUES (?, ?, ?, ?, ?);"
        # The n.noteid here is the note id for the actual note that is
        # being auto-saved.  The temp note id that refers to the
        # newly created note will be returned.
        args = (n.noteid, n.subject, n.notedata, n.tagstring, n.url)
        cur.execute(q, args)
        tmpnoteid = cur.lastrowid
        con.commit()
        cur.close()
        con.close()
        return tmpnoteid

    def update_temp_note(self, n):
        """Update a temporary note.

        update_temp_note(n)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "UPDATE temp_notes SET subject = ?, notedata = ?, tags = ?," \
            "url = ?" \
            "WHERE id = ?;"
        # At this point the n.noteid is the id for the temp note.
        # Don't need to reuse the backed up note id because it should
        # already be in the temp_notes db record and it's not being
        # changed but we do need the temp note's id to update it.
        args = (n.subject, n.notedata, n.tagstring, n.url, n.noteid)
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()
        logger.info("Update completed!")

    def delete_temp_note(self, nid, id_is_noteid=False):
        """Delete temporary note.

        delete_temp_note(nid, id_is_noteid=False)
        """
        logger.info("Deleting temp note %d..." % nid)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        if id_is_noteid:
            q = "DELETE FROM temp_notes WHERE noteid = ?;"
        else:
            q = "DELETE FROM temp_notes WHERE id = ?;"
        args = [nid]
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()
        logger.info("Delete completed!")

    def get_temp_note(self, nid):
        """Get auto-saved temp note by note's (and NOT temp note's) id.

        get_temp_note(nid)
        """
        n = note()
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT subject, tags, url, notedata " \
            "FROM temp_notes WHERE noteid = ?;"
        args = (nid,)
        cur.execute(q, args)
        result = cur.fetchone()
        cur.close()
        con.close()

        if result:
            n.noteid = nid
            n.subject = result[0]
            n.tagstring = result[1]
            n.url = result[2]
            n.notedata = result[3]
            return n

    def select_note(self, noteid):
        """ Select the note associated with the passed id.

        select_note(noteid)
        """
        self.currentNote = self.get_note(noteid)

    def select_new_note(self):
        """Select the most recent note within the notebook.

        select_new_note()
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT id FROM notes ORDER BY crtime DESC;"
        cur.execute(q)
        results = cur.fetchone()
        newnote = results[0]
        cur.close()
        con.close()
        self.select_note(newnote)

    def get_all_notes(self):
        """Retrieve all of the notes from the notebook as list of note objects.
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT id, subject, url, crtime, mtime, notedata FROM notes;"
        cur.execute(q)
        results = cur.fetchall()

        cur.close()
        con.close()

        return [note(noteid=r[0], subject=r[1], url=r[2], crtime=r[3],
            mtime=r[4], notedata=r[5]) for r in results]

    def get_note(self, noteid):
        """ Get a note by its id.

        get_note(noteid)
        """
        # see if this note is already selected
        #if id == self.currentNote.id:
            #return self.currentNote
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT id, subject, datetime(crtime, 'localtime'), " \
            "datetime(mtime, 'localtime'), url, notedata " \
            "FROM notes WHERE id = ?;"
        # "Incorrect number of bindings supplied" when I do it with
        # the ? and a string
        #cur.execute(q, (str(id)))
        args = [noteid]
        cur.execute(q, args)
        rnote = cur.fetchone()
        if rnote is not None:
            n = note()
            n.noteid = rnote[0]
            n.subject = rnote[1]
            n.crtime = rnote[2]
            n.mtime = rnote[3]
            n.url = rnote[4]
            n.notedata = rnote[5]
            # now get tags
            q = "SELECT tags.name FROM tags INNER JOIN (SELECT tag FROM " \
                "notes_tags WHERE notes_tags.note = ?) AS tag_ids " \
                "ON tags.id = tag_ids.tag;"
            args = [n.noteid]
            cur.execute(q, args)
            results = cur.fetchall()
            for i in results:
                n.tags.add(i[0])
        cur.close()
        con.close()
        if rnote is None:
            return None
        else:
            return n

    def get_preview_items(self):
        """ Get a listing of notes for the notes list preview.

        If tags have been applied to the notebook, they will be used
        to filter the listing."""
        #count = self.count()
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        taglist = list(self.tags)
        if not taglist:
            # run this query if there aren't any filter tags listed
            #if count > 50: # This is buggy and needs to be fixed.
            # Disable for now.
            if False:
                q = "SELECT subject, datetime(crtime, 'localtime'), " \
                    "datetime(mtime, 'localtime'), id, url" \
                    "FROM (SELECT * FROM " \
                    "notes ORDER BY crtime DESC, id DESC LIMIT 80) " \
                    "AS new_notes ORDER BY crtime ASC, id ASC;"
            else:
                q = "SELECT subject, datetime(crtime, 'localtime'), " \
                    "datetime(mtime, 'localtime'), id, url FROM notes " \
                    "ORDER BY crtime ASC, id ASC"
            #q = "SELECT subject, datetime(crtime, 'localtime'), " \
            # "datetime(mtime, 'localtime'), id FROM notes " \
            # "ORDER BY crtime ASC, id ASC LIMIT 500;"
            cur.execute(q)
        else:
            name_clause = ""
            i = 0
            for t in taglist:
                if i == len(taglist) - 1:
                    name_clause += "name = ?"
                else:
                    # should it use OR or AND?
                    name_clause += "name = ? AND "
                i += 1
            q = "SELECT subject, datetime(crtime, 'localtime'), " \
                "datetime(mtime, 'localtime'), id, url FROM notes INNER JOIN "\
                "(SELECT note FROM notes_tags WHERE tag = (SELECT id " \
                "FROM tags WHERE %s)) AS matching_notes ON " \
                "notes.id = matching_notes.note;" % name_clause
            args = taglist
            cur.execute(q, args)
        results = cur.fetchall()
        preview_items = [note(subject=r[0], crtime=r[1], mtime=r[2],
            noteid=r[3], url=r[4]) for r in results]
        cur.close()
        con.close()
        #logger.info(preview_items)
        return preview_items

    def get_all_deleted_notes(self):
        """Get id, deleted timestamp, and subject for all deleted notes."""
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT id, deltime, subject FROM trash;"
        cur.execute(q)
        trash = cur.fetchall()
        cur.close()
        con.close()
        return [note(noteid=r[0], deltime=r[1], subject=r[2]) for r in trash]

    def get_note_subjects(self):
        """Get all of the subjects and ids for the notes."""
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT id, subject FROM notes;"
        cur.execute(q)
        notes = cur.fetchall()
        cur.close()
        con.close()
        return [note(noteid=r[0], subject=r[1]) for r in notes]

    def get_deleted_note(self, nid):
        """Get specified deleted note from trash.

        get_deleted_note(nid)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT crtime, mtime, deltime, subject, notedata, tags " \
            "FROM trash WHERE id = ?;"
        args = (nid,)
        cur.execute(q, args)
        n = cur.fetchone()
        cur.close()
        con.close()
        logger.info(n)
        return note(crtime=n[0], mtime=n[1], deltime=n[2], subject=n[3],
            notedata=n[4], tagstring=n[5])

    def undelete_note(self, nid):
        """Undelete note by id.

        undelete_note(nid)
        """
        # get note from trash
        n = self.get_deleted_note(nid)

        logger.info("Found this note: %s" % str(n))

        # add note again
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        # TODO:  save id when deleting note, in the future i might want to
        # add linking between notes using the id to correspond to another
        # note, right now they're just used internally for editing/deleting
        # and whatnot, but in the future i could use them to actually
        # identify other notes for doing other things
        #q = "INSERT INTO notes (id, crtime, mtime, subject, note)
        # VALUES(?, ?, ?, ?, ?);"
        q = "INSERT INTO notes (crtime, mtime, subject, notedata, url) " \
            "VALUES(?, ?, ?, ?, ?);"
        args = (n.crtime, n.mtime, n.subject, n.notedata, n.url)
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()

        logger.info("About to delete the note now,"
            "it should have been restored.")

        # now remove the note from the trash
        self.delete_trash_note(nid)

        logger.info("adding tags?")

        # if there are any tags, add them
        if n.tags:
            self.select_new_note()
            self.update_tags(n.tagstring)

    def delete_trash_note(self, nid):
        """Permanently delete note from trash.

        delete_trash_note(nid)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "DELETE FROM trash WHERE id = ?;"
        args = (nid,)
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()

    def empty_trash(self):
        """Empty the trash (deleted notes)."""
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "DELETE FROM trash;"
        cur.execute(q)
        con.commit()
        cur.close()
        con.close()

    def get_notedata(self, noteid):
        """Get the note text content for the specified note.

        get_notedata(noteid)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT notedata FROM notes WHERE id = ?;"
        args = [noteid]
        cur.execute(q, args)
        cur.close()
        con.close()
        return note(notedata=cur.fetchone()[0])

    def update_note(self, n):
        """ Update a note in the database.

        update_note(n)
        """
        logger.info("Updating note...")
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "UPDATE notes SET subject = ?, notedata = ? , url = ?" \
            "WHERE id = ?;"
        args = (n.subject, n.notedata, n.url, n.noteid)
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()
        logger.info("Update completed!")

    def delete_note(self, noteid):
        """Delete the note that has the passed id.

        delete_note(noteid)
        """
        logger.info("Deleting note %d..." % noteid)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "DELETE FROM notes WHERE id = ?;"
        args = [noteid]
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()
        logger.info("Delete completed!")

    def vacuum(self):
        """Vacuum the notebook database."""
        logger.info("Vacuuming the notes db...")
        try:
            con = sqlite3.connect(self.db)
            cur = con.cursor()
            q = "VACUUM;"
            cur.execute(q)
            con.commit()
            cur.close()
            con.close()
            logger.info("Vacuum completed!")
        except Exception as ex:
            logger.info("Exception: %s" % ex)
            logger.exception(ex)
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

    def add_tag(self, tag):
        """ Pass a tag and it gets inserted into the tags table;

        add_tag(tag)

        returns the tag id """
        if tag == "":
            return None
        #logger.info("About to insert tag: %s" % tag)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "INSERT INTO tags (name) VALUES (?);"
        cur.execute(q, (tag,))
        newtagid = cur.lastrowid
        con.commit()
        cur.close()
        con.close()
        # tag should now be inserted
        return newtagid

    def get_tag_id(self, tag):
        """Get the id for a tag.

        get_tag_id(tag)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT id FROM tags WHERE name = ?;"
        args = [tag]
        cur.execute(q, args)
        results = cur.fetchone()
        cur.close()
        con.close()
        if results is not None:
            return results[0]
        else:
            return None

    def get_tags(self, noteid):
        """Get all the tag ids associated with a note id.

        get_tags(noteid)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        q = "SELECT tag FROM notes_tags WHERE note = ?"
        cur.execute(q, (noteid,))
        cur.fetchall()

        cur.close()
        con.close()

    def add_note_tags(self, noteid, newtags):
        """Add the tags in tuple newtags to the specified note.

        add_note_tags(noteid, newtags)
        """

        # make sure there is an id and some tags being passed
        if not noteid:
            logger.info("no note id? %d" % (noteid))
            return
        if not newtags:
            logger.info("no tags? %s" % (newtags))
            return

        # find current tag associations by getting ids for current tags
        notestags = self.get_tags(noteid)
        removedtags = None
        if notestags:
            oldtags = set(i[0] for i in notestags)
            removedtags = newtags - oldtags

        newtagids = set()
        # get tag ids for new tags
        for tag in newtags:
            #logger.info("Tag = {}".format(tag))
            t = self.get_tag_id(tag)
            if t:
                # add tag
                newtagids.add(t)
                #logger.info("tagid = {}".format(t))
            else:
                # insert the tag
                newtagid = self.add_tag(tag)
                newtagids.add(newtagid)
                #logger.info("tagid = {}".format(newtagid))

        # open up db
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        # get rid of removed tag relationships
        if removedtags:
            args = tuple((noteid, i) for i in removedtags)
            q = "DELETE FROM notes_tags WHERE note = ? AND tag = ?;"
            cur.executemany(q, args)

        # add tag relationships to notes_tags
        args = tuple((noteid, i) for i in newtagids)
        q = "INSERT INTO notes_tags (note, tag) VALUES (?, ?);"
        cur.executemany(q, args)

        con.commit()
        cur.close()
        con.close()

    def update_tags(self, s):
        """ Pass a space-delimited string and turn it into tags.

        update_tags(s)
        """
        logger.info("Tags: %s" % s)
        #self.ClearTags()
        if s == "":
            logger.info("Blank tag.  Returning.")
            self.clear_tags()
            return

        tags = s.split(" ")
        logger.info("Tags split: %s" % (str(tags)))
        tagsToRemove = []
        # go through new tags
        for i in self.currentNote.oldtags:
            if i not in tags:
                logger.info("Found tag -->%s<-- no longer being used." % i)
                tagsToRemove.append(i)

        con = sqlite3.connect(self.db)
        cur = con.cursor()

        # delete old tag relationships
        for t in tagsToRemove:
            q = "SELECT id FROM tags WHERE name = ?;"
            args = [t]
            cur.execute(q, args)
            tagid = cur.fetchone()[0]
            q = "DELETE FROM notes_tags WHERE tag = ?;"
            args = [tagid]
            cur.execute(q, args)
            con.commit()

        # go through all tags
        for t in tags:
            # ignore any "empty" tags
            if t == "":
                continue
            # if tag relationship already exists, skip it
            if t in self.currentNote.oldtags:
                logger.info("Found pre-existing tag relationship -->%s<--."
                    % t)
                continue
            # find the id
            tagid = self.get_tag_id(t)
            if tagid is None:
                # if the tag doesn't exist, add it
                self.add_tag(t)
                # and get the id again
                tagid = self.get_tag_id(t)
                if tagid is None:
                    logger.info("Serious problems.")
                    return -1
            logger.info("note=%d, tag=%d" % (self.currentNote.noteid, tagid))
            # now update the tags_notes
            q = "INSERT INTO notes_tags (note, tag) VALUES (?, ?);"
            args = (self.currentNote.noteid, tagid)
            cur.execute(q, args)
            con.commit()
        cur.close()
        con.close()

    def clear_tags(self):
        """ Clear all tags associated with current note.
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "DELETE FROM notes_tags WHERE note = ?;"
        args = [self.currentNote.noteid]
        cur.execute(q, args)
        con.commit()
        cur.close()
        con.close()

    def get_all_tags(self):
        """Get all of the tag names being used in the notebook.
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        q = "SELECT name FROM tags;"
        cur.execute(q)
        results = cur.fetchall()
        logger.info(results)
        return results

    def add_test_notes(self, n=10, delay=0, tags=0):
        """ Create sample notes for testing purposes.

        add_test_notes(n=10, delay=0, tags=0)

        n is the number of notes to create.
        delay is how many seconds to wait between creating notes.
        tags is how many tags to add to each note.
        """
        for i in range(1, n + 1):
            n = note()
            n.subject = "Subject %d" % i
            n.notedata = "Note text %d" % i
            n.url = r"https://www.bitbucket.org/"
            nid = self.add_note(n)
            if tags > 0:
                for i in range(1, tags + 1):
                    n.tags.add(chr(random.randint(65, 90)) * 5)
                self.add_note_tags(nid, n.tags)
            if delay:
                time.sleep(delay)

    def find(self, s):
        """Find the string s in the notebook.

        find(s)
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()

        logger.info("Looking for -->%s<--" % s)

        q = "SELECT subject, datetime(crtime, 'localtime'), " \
            "datetime(mtime, 'localtime'), id FROM notes WHERE subject " \
            "LIKE ? OR notedata LIKE ? ORDER BY crtime ASC;"
        arg = '%' + s + '%'
        args = (arg, arg)
        logger.info("args = ")
        logger.info(args)
        cur.execute(q, args)

        logger.info("Row count: %d" % cur.rowcount)

        results = cur.fetchall()
        cur.close()
        con.close()
        logger.info(results)
        return [note(subject=r[0], crtime=r[1], mtime=r[2], noteid=r[3])
            for r in results]


def main():
    notebook_name = "poppycock.db"
    if os.path.exists(notebook_name):
        os.remove(notebook_name)
    notes = notebook(notebook_name, create=True)

if __name__ == "__main__":
    main()
