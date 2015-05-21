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


class TrashFrame(wx.Frame):
    def __init__(self, parent, id, title, db):
        wx.Frame.__init__(self, parent, id, title, size=(450, 400))

        self.sdb = db

        trash = self.sdb.get_all_deleted_notes()
        if trash:
            del_notes = ["%s %s" % (n.deltime, n.subject) for n in trash]
            self.del_ids = [n.noteid for n in trash]
            print("Deleted notes ids: ")
            print(str(self.del_ids))
        else:
            raise Exception("There are currently no deleted notes.")

        # set up splitter
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        self.splitter.SetMinimumPaneSize(175)

        # set up panels
        self.listpanel = wx.Panel(self.splitter, -1, style=wx.BORDER_SUNKEN)
        self.notepanel = wx.Panel(self.splitter, -1, style=wx.BORDER_SUNKEN)

        # create some widgets
        self.delitems = wx.ListBox(self.listpanel, -1, choices=del_notes,
           size=(100, 100), style=wx.LB_SINGLE | wx.LB_HSCROLL)
        spaces = 40
        self.created = wx.StaticText(self.notepanel, -1, ' ' * spaces)
        self.edited = wx.StaticText(self.notepanel, -1, ' ' * spaces)
        self.deleted = wx.StaticText(self.notepanel, -1, ' ' * spaces)
        self.subject = wx.StaticText(self.notepanel, -1, ' ' * spaces)
        self.tags = wx.StaticText(self.notepanel, -1, ' ' * spaces)
        self.content = wx.TextCtrl(self.notepanel, -1,
            "Please select a note.", style=wx.TE_MULTILINE)
        self.undelete = wx.Button(self.notepanel, -1, "Undelete")
        self.undelete.SetToolTip(wx.ToolTip("Undelete the currently"
            "selected note."))
        self.permadelete = wx.Button(self.notepanel, -1, "Delete")
        self.permadelete.SetToolTip(wx.ToolTip("Permanently delete the"
            "currently selected note."))
        self.empty = wx.Button(self.notepanel, -1, "Empty trash")
        self.empty.SetToolTip(wx.ToolTip("Permanently delete all notes in"
            "the trash."))

        self.Bind(wx.EVT_LISTBOX, self.OnListItemSelected, self.delitems)
        self.Bind(wx.EVT_BUTTON, self.OnUndelete, self.undelete)
        self.Bind(wx.EVT_BUTTON, self.OnPermaDelete, self.permadelete)
        self.Bind(wx.EVT_BUTTON, self.OnEmptyTrash, self.empty)

        # set up the sizers
        vboxlist = wx.BoxSizer(wx.VERTICAL)
        vboxlist.Add(self.delitems, 1, wx.ALL | wx.EXPAND |
            wx.ALIGN_CENTER_HORIZONTAL, 5)

        vboxnote = wx.BoxSizer(wx.VERTICAL)

        hboxdates = wx.BoxSizer(wx.HORIZONTAL)

        hboxdates.Add(self.created, 0, wx.ALL | wx.FIXED_MINSIZE, 5)
        hboxdates.Add(self.edited, 0, wx.ALL | wx.FIXED_MINSIZE, 5)
        hboxdates.Add(self.deleted, 0, wx.ALL | wx.FIXED_MINSIZE, 5)
        vboxnote.Add(hboxdates, 0)

        vboxnote.Add(self.subject, 0, wx.ALL | wx.FIXED_MINSIZE, 5)
        vboxnote.Add(self.tags, 0, wx.ALL | wx.FIXED_MINSIZE, 5)
        vboxnote.Add(self.content, 1, wx.ALL | wx.EXPAND, 5)

        hboxbuttons = wx.BoxSizer(wx.HORIZONTAL)
        hboxbuttons.Add(self.undelete, 0, wx.ALL, 5)
        hboxbuttons.Add(self.permadelete, 0, wx.ALL, 5)
        hboxbuttons.Add(self.empty, 0, wx.ALL, 5)

        # if the 2nd arg is 1, it won't align on the bottom
        vboxnote.Add(hboxbuttons, 0, wx.ALIGN_CENTRE | wx.ALIGN_BOTTOM)

        self.listpanel.SetSizer(vboxlist)
        self.notepanel.SetSizer(vboxnote)
        self.listpanel.SetFocus()

        # set up the splitter
        self.splitter.SplitVertically(self.listpanel, self.notepanel)
        self.splitter.Unsplit()
        self.listpanel.SetFocus()

        #self.SetClientSize(self.listpanel.GetBestSize())
        self.Centre()
        self.Show(True)

        self.splitter.SplitHorizontally(self.listpanel, self.notepanel)
        #self.listpanel.SetFocus()

        self.selectedID = -1

    def PopulateNotesList(self):
        trash = self.sdb.get_all_deleted_notes()
        if trash:
            del_notes = [" ".join([str(i[j]) for j in range(1, 3)])
                for i in trash]
            self.del_ids = [i[0] for i in trash]
            print("Deleted notes ids: ")
            print(str(self.del_ids))
        else:
            raise Exception("There are currently no deleted notes.")
        self.delitems.InsertItems(del_notes)

    def OnListItemSelected(self, e):

        #d = dir(e)
        #self.content.ChangeValue("string: " + str(e.GetSelection()))
        #self.content.ChangeValue(str(d))

        print("Selection: %s" % str(e.GetSelection()))
        self.selectedID = self.del_ids[e.GetSelection()]
        print("Selected id = %d" % self.selectedID)
        n = self.sdb.get_deleted_note(self.selectedID)
        #print("note = {}".format(n))
        self.UpdateValues(n.crtime, n.mtime, n.deltime, n.subject, n.notedata,
            n.tagstring)

    def UpdateValues(self, cr='', ed='', dlt='', sub='', cont='', tags=''):
        """Update values for currently selected note."""
        self.created.SetLabel("Created: " + cr)
        self.edited.SetLabel("Modified: " + ed)
        self.deleted.SetLabel("Deleted: " + dlt)
        self.subject.SetLabel("Subject: " + sub)
        if tags:
            self.tags.SetLabel("Tags: " + tags)
        if len(cont) < 1024:
            self.content.ChangeValue(cont)
        else:
            self.content.ChangeValue(cont[:1024] +
                "\n\n...MORE REMAINING IN NOTE...")

    def OnUndelete(self, e):
        print("called undelete")
        # TODO:  CONFIRMATION?
        self.sdb.undelete_note(self.selectedID)

        self.delitems.Clear()
        self.UpdateValues()

    def OnPermaDelete(self, e):
        print("called perma delete")
        # TODO:  CONFIRMATION?
        self.sdb.delete_trash_note(self.selectedID)
        self.delitems.Clear()
        self.UpdateValues()

    def OnEmptyTrash(self, e):
        print("called empty trash")
        # TODO:  CONFIRMATION?
        self.sdb.empty_trash()
        self.delitems.Clear()
        self.UpdateValues()
