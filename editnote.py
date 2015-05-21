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

import wx
from edittags import EditTagsFrame
from snatcher import note

ID_BTN_SAVENOTE = wx.NewId()
ID_BTN_CANCEL = wx.NewId()
ID_BTN_PREV = wx.NewId()
ID_BTN_NEXT = wx.NewId()
ID_BTN_EDITTAGS = wx.NewId()
ID_BTN_OPENURL = wx.NewId()

class EditNoteFrame(wx.Dialog):
    def __init__(self, parent, id, title, db, noteid=None):
        wx.Dialog.__init__(self, parent, id, title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.sdb = db
        if noteid:
            self.current_note_id = noteid
        else:
            self.current_note_id = -1

        # widgets
        self.txtSubject = wx.TextCtrl(panel, -1, size=(300, -1))

        # url
        urlbox = wx.BoxSizer(wx.HORIZONTAL)

        self.txtURL = wx.TextCtrl(panel, -1, size=(300, -1),
            style=wx.TE_AUTO_URL)
        btnGo = wx.Button(panel, ID_BTN_OPENURL, "Go")
        btnGo.SetToolTip(wx.ToolTip("Launch URL in your default browser."))
        urlbox.Add(self.txtURL, 0)
        urlbox.Add(btnGo, 0)

        # tag stuff
        tagbox = wx.BoxSizer(wx.HORIZONTAL)

        self.txtTags = wx.TextCtrl(panel, -1, size=(300, -1))
        btnEditTags = wx.Button(panel, ID_BTN_EDITTAGS, "Tags")
        btnEditTags.SetToolTip(wx.ToolTip("Edit tags."))
        tagbox.Add(self.txtTags, 0)
        tagbox.Add(btnEditTags, 0)

        self.txtNote = wx.TextCtrl(panel, -1, "", size=(400, 300),
            style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_AUTO_URL)
        self.timestamp = wx.StaticText(panel, -1, size=(400, -1))

        # buttons
        btnSaveNote = wx.Button(panel, wx.ID_OK, "Save")
        btnCancel = wx.Button(panel, wx.ID_CANCEL)
        # buttons sizer
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        bbox.Add(btnSaveNote, 0, wx.ALL, 5)
        bbox.Add(btnCancel, 0, wx.ALL, 5)

        # sizer
        vbox.Add(self.timestamp, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)
        vbox.Add(self.txtSubject, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)
        vbox.Add(urlbox, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)
        vbox.Add(tagbox, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)
        vbox.Add(self.txtNote, 1, wx.LEFT | wx.TOP | wx.RIGHT | wx.EXPAND, 5)
        vbox.Add(bbox, 0, wx.ALIGN_CENTRE | wx.ALIGN_BOTTOM)

        # events
        self.Bind(wx.EVT_BUTTON, self.OnEditTags, id=ID_BTN_EDITTAGS)
        self.Bind(wx.EVT_BUTTON, self.OnOpenURL, id=ID_BTN_OPENURL)

        panel.SetSizer(vbox)
        self.SetClientSize(panel.GetBestSize())

        self.parent = parent
        self.currentidx = 0
        self.max = self.sdb.count() - 1
        self.sdb.currentNote.oldtags = self.sdb.currentNote.tags.copy()

        self.temp_id = None
        self.save_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        """seems to be a bug on linux where even though the changevalue
        method being used in shownote shouldn't trigger the wx.EVT_TEXT
        event, it does anyway so update the fields with the notes before
        binding the event
        """
        self.ShowNote()

        self.Bind(wx.EVT_TEXT, self.OnTextEntered, self.txtNote)

    def ClearText(self):
        """ Clear all the widgets """
        self.txtSubject.Clear()
        self.txtNote.Clear()
        self.txtTags.Clear()
        self.txtURL.Clear()

    def ShowNote(self):
        """ Get the current note and show it """
        self.ClearText()
        if self.current_note_id != -1:
            timestamp = "Created: %s\tModified: %s" % \
              (self.sdb.currentNote.crtime, self.sdb.currentNote.mtime)
        else:
            timestamp = ""

        self.timestamp.SetLabel(timestamp)

        self.txtSubject.ChangeValue(self.sdb.currentNote.subject)
        self.txtURL.ChangeValue(self.sdb.currentNote.url)
        self.txtNote.ChangeValue(self.sdb.currentNote.notedata)
        self.txtTags.ChangeValue(self.sdb.currentNote.get_tags_string())
        print "This is the tags converted to string:"
        #print self.sdb.currentNote.get_tags_string()
        # this is for restored temp notes
        if self.sdb.currentNote.tagstring:
            self.txtTags.ChangeValue(self.sdb.currentNote.tagstring)
            print "This is the tagstring:"
            print self.sdb.currentNote.tagstring

        self.txtNote.ShowPosition(0)

    def OnEditTags(self, e):

        oldtags = self.sdb.currentNote.tags.copy()

        edittags = EditTagsFrame(self, -1, "Edit Tags", "note", self.sdb)
        edittags.Centre()
        val = edittags.ShowModal()
        if val == wx.ID_OK:
            self.txtTags.Clear()
            self.txtTags.WriteText(self.sdb.currentNote.get_tags_string())
        else:
            # restore old tags
            self.sdb.currentNote.tags = oldtags.copy()
        edittags.Destroy()

    def OnOpenURL(self, e):
        """Open the url in the default browser.
        """
        pass

    def OnTextEntered(self, e):
        """Text has changed."""
        print("text changed, starting timer to autosave")
        self.save_timer.Start(5000)

    def OnTimer(self, e):
        print("timer is firing")
        self.save_timer.Stop()
        n = self.get_note_fields()
        if not self.temp_id:
            print("creating new auto-saved temp note")
            # save all fields to new temp note
            # be sure to save the note's id
            n.noteid = self.current_note_id
            # be sure to get temp note's ID and set it to self.temp_id
            self.temp_id = self.sdb.add_temp_note(n)
        else:
            print("updating auto-saved temp note")
            # save all fields to temp note
            n.noteid = self.temp_id
            self.sdb.update_temp_note(n)
            # TODO:  watch out for problems here, does the constraint
            # that replaces previous temp_notes cause problems?
            # if so, re-set the id

    def get_note_fields(self):
        """Get the text from all of the fields"""
        print("getting text from fields")
        n = note()
        n.subject = self.txtSubject.GetValue()
        n.url = self.txtURL.GetValue()
        n.tagstring = self.txtTags.GetValue()
        n.tags = n.tagstring.split()
        n.notedata = self.txtNote.GetValue()
        return n
