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

ID_BTN_ADDTAG = wx.NewId()
ID_BTN_ADDUSE = wx.NewId()
ID_BTN_USETAG = wx.NewId()
ID_BTN_REMTAG = wx.NewId()
ID_BTN_DELTAG = wx.NewId()
ID_BTN_SAVETAGS = wx.NewId()
ID_TE_ADDTAG = wx.NewId()
ID_LST_ALL = wx.NewId()
ID_LST_CURRENT = wx.NewId()

class EditTagsFrame(wx.Dialog):
    def __init__(self, parent, id, title, mode, db):
        wx.Dialog.__init__(self, parent, id, title + " " + mode + " Mode",
            style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.mode = mode
        self.sdb = db
        panel = wx.Panel(self, -1, size=(500, 500))
        # sizers
        vbox = wx.BoxSizer(wx.VERTICAL)
        newtagbox = wx.BoxSizer(wx.HORIZONTAL)
        tagcopybox = wx.BoxSizer(wx.HORIZONTAL)
        alltagsbox = wx.BoxSizer(wx.VERTICAL)
        currenttagsbox = wx.BoxSizer(wx.VERTICAL)
        tagbtnsbox = wx.BoxSizer(wx.VERTICAL)
        bottombtns = wx.BoxSizer(wx.HORIZONTAL)

        # widgets
        lblNewTag = wx.StaticText(panel, -1, "New Tag:")

        self.txtNewTag = wx.TextCtrl(panel, ID_TE_ADDTAG, size=(100, -1),
            style=wx.TE_PROCESS_ENTER)
        btnAddTag = wx.Button(panel, ID_BTN_ADDTAG, "Add Tag")
        btnAddTag.SetToolTip(wx.ToolTip("Add a new tag."))

        lblAllTags = wx.StaticText(panel, -1, "All Tags:")
        self.lstAllTags = wx.ListBox(panel, ID_LST_ALL, size=(130, 200),
            style=wx.LB_SINGLE | wx.LB_SORT | wx.LB_HSCROLL)

        btnUseTag = wx.Button(panel, ID_BTN_USETAG, "Use ->")
        btnUseTag.SetToolTip(wx.ToolTip("Use the currently selected tag."))
        btnRemoveTag = wx.Button(panel, ID_BTN_REMTAG, "<- Remove")
        btnRemoveTag.SetToolTip(wx.ToolTip("Don't use the currently"
            "selected tag."))
        btnDelTag = wx.Button(panel, ID_BTN_DELTAG, "Delete")
        btnDelTag.SetToolTip(wx.ToolTip("Delete the selected tag from"
            "the notebook."))
        btnSaveTags = wx.Button(panel, wx.ID_OK)
        btnCancel = wx.Button(panel, wx.ID_CANCEL)

        lblCurrentTags = wx.StaticText(panel, -1, "Current Tags:")
        self.lstCurrentTags = wx.ListBox(panel, ID_LST_CURRENT,
            size=(130, 200), style=wx.LB_SINGLE | wx.LB_SORT | wx.LB_HSCROLL)

        newtagbox.Add(self.txtNewTag, 0, wx.LEFT | wx.EXPAND, 10)
        newtagbox.Add(btnAddTag, 0, wx.LEFT | wx.EXPAND, 10)

        alltagsbox.Add(lblAllTags, 0, wx.LEFT, 10)
        alltagsbox.Add(self.lstAllTags, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        tagbtnsbox.Add((-1, 10))
        tagbtnsbox.Add(btnUseTag, 0, wx.ALIGN_LEFT)
        tagbtnsbox.Add(btnRemoveTag, 0, wx.ALIGN_LEFT)
        tagbtnsbox.Add((-1, 10))
        tagbtnsbox.Add(btnDelTag, 0, wx.ALIGN_LEFT)

        currenttagsbox.Add(lblCurrentTags, 0, wx.LEFT, 10)
        currenttagsbox.Add(self.lstCurrentTags, 0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        tagcopybox.Add(alltagsbox, 0)
        tagcopybox.Add(tagbtnsbox, 0,
            wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL)
        tagcopybox.Add(currenttagsbox, 0)

        bottombtns.Add(btnSaveTags, 0)
        bottombtns.Add(btnCancel, 0)

        vbox.Add(lblNewTag, 0, wx.LEFT | wx.TOP, 10)
        vbox.Add(newtagbox, 0)
        vbox.Add((-1, 10), 0)
        vbox.Add(tagcopybox, 1, wx.EXPAND)
        vbox.Add(bottombtns, 0, wx.ALIGN_CENTER)

        #self.SetClientSize(panel.GetBestSize())

        size = wx.Size(400, 300)
        self.SetSize(size)
        panel.SetSizer(vbox)

        vbox.Fit(self)
        self.Layout()

        # events
        # buttons
        self.Bind(wx.EVT_TEXT_ENTER, self.OnAddTag, self.txtNewTag)
        self.Bind(wx.EVT_BUTTON, self.OnAddTag, id=ID_BTN_ADDTAG)
        self.Bind(wx.EVT_BUTTON, self.OnUseTag, id=ID_BTN_USETAG)
        self.Bind(wx.EVT_BUTTON, self.OnRemTag, id=ID_BTN_REMTAG)
        self.Bind(wx.EVT_BUTTON, self.OnDelTag, id=ID_BTN_DELTAG)

        # list box events
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnUseTag, id=ID_LST_ALL)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRemTag, id=ID_LST_CURRENT)

        # show the tags
        self.ShowTags()

    def OnAddTag(self, e):
        pass
        print("OnAddTag")

        newtag = self.txtNewTag.GetValue()
        if newtag == "":
            return
        print("New tag: %s" % newtag)

        if self.mode == "note":
            # if tag is not in current note's tags
            if newtag not in self.sdb.currentNote.tags:
                # add tag text to current note's tags
                self.sdb.currentNote.tags.add(newtag)
                # add that tag to current tag list box
                self.lstCurrentTags.Append(newtag)
            else:
                print("Current tags: %s" %
                    (self.sdb.currentNote.get_tags_string()))
        elif self.mode == "notelist":
            if newtag not in self.sdb.tags:
                self.sdb.tags.add(newtag)
                self.lstCurrentTags.Append(newtag)
                print("tag added to self.sdb.tags: %s" % newtag)
            else:
                print("Current tags: %s" % (self.sdb.tags.get_tags_string()))
        self.txtNewTag.Clear()
        self.txtNewTag.SetFocus()

    def OnUseTag(self, e):
        pass
        print("OnUseTag")
        sel = self.lstAllTags.GetSelection()
        if sel == -1:
            return
        # get selected tag item from list box
        seltag = self.lstAllTags.GetString(sel)

        if self.mode == "notelist":
            # add that tag to db tags
            # update main form's listing
            if seltag not in self.sdb.tags:
                self.lstCurrentTags.Append(seltag)
                self.sdb.tags.add(seltag)
                #print("tag added to self.sdb.tags: %s" % seltag)
        elif self.mode == "note":
            pass
            if seltag not in self.sdb.currentNote.tags:
                self.lstCurrentTags.Append(seltag)
                self.sdb.currentNote.tags.add(seltag)

    def OnRemTag(self, e):
        print("OnRemTag")
        # get selected tag item from list box
        sel = self.lstCurrentTags.GetSelection()
        if sel == -1:
            return

        if self.mode == "notelist":
            pass
            # get selected item from list box
            # remove that tag from db tags
            # remove that tag from list box
            # update main form's listing
            seltag = self.lstCurrentTags.GetString(sel)
            # remove that tag from list box
            self.lstCurrentTags.Delete(sel)
            # remove that tag from current note's tags
            self.sdb.tags.remove(seltag)
        elif self.mode == "note":
            # get tag
            seltag = self.lstCurrentTags.GetString(sel)
            # remove that tag from list box
            self.lstCurrentTags.Delete(sel)
            # remove that tag from current note's tags
            self.sdb.currentNote.tags.remove(seltag)

    def OnDelTag(self, e):
        print("OnDelTag")
        # get selected tag
        if self.mode == "notelist":
            pass
            # remove it from both list boxes
        elif self.mode == "note":
            pass
            # remove it from both list boxes
        # remove every relationship that involves that tag

    def ShowTags(self):
        # get all tags from tags table
        tags = [t[0] for t in self.sdb.get_all_tags()]
        # all tags from current note
        # loop through them
        for t in tags:
            # add it to available tags
            self.lstAllTags.Append(t)
            if self.mode == "notelist":
                if t in self.sdb.tags:
                    self.lstCurrentTags.Append(t)
            elif self.mode == "note":
                # if tag is part of current note's tags
                if t in self.sdb.currentNote.tags:
                    # add it to current tags
                    self.lstCurrentTags.Append(t)
