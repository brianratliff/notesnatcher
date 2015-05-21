#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       snatchergui.py
#
#       The Snatcher main gui stuff
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
import sys
import wx
if 'win' in sys.platform:
    from wx.lib.mixins.listctrl import ListRowHighlighter

import snatcher
from editnote import EditNoteFrame
from edittags import EditTagsFrame
from trash import TrashFrame
from options import OptionsFrame

__title__ = "Note Snatcher"
__author__ = "Brian Ratliff"

icons_path = "icons/"

ID_FILEMENU_NEW = wx.NewId()
ID_FILEMENU_OPEN = wx.NewId()
ID_FILEMENU_IMPORT = wx.NewId()
ID_FILEMENU_IMPORT_SXML = wx.NewId()
ID_FILEMENU_IMPORT_CINTA = wx.NewId()
ID_FILEMENU_EXPORT = wx.NewId()
ID_FILEMENU_EXPORT_SXML = wx.NewId()
ID_FILEMENU_EXPORT_CINTA = wx.NewId()
ID_FILEMENU_EXPORT_HTML = wx.NewId()
ID_FILEMENU_EXIT = wx.NewId()
ID_FILEMENU_OPTIONS = wx.NewId()

ID_NOTESMENU_NEW = wx.NewId()
ID_NOTESMENU_EDIT = wx.NewId()
ID_NOTESMENU_DEL = wx.NewId()
ID_NOTESMENU_VAC = wx.NewId()
ID_NOTESMENU_PROP = wx.NewId()
ID_NOTESMENU_TRASH = wx.NewId()
ID_NOTESMENU_EMPTYTRASH = wx.NewId()

ID_VIEWMENU_SHOWALL = wx.NewId()
ID_VIEWMENU_FILTER = wx.NewId()
ID_VIEWMENU_REFRESH = wx.NewId()
ID_VIEWMENU_SHOWHIDENOTE = wx.NewId()
ID_VIEWMENU_LISTCTRL = wx.NewId()
ID_VIEWMENU_LISTBOX = wx.NewId()

ID_BTN_NEWNOTE = wx.NewId()
ID_BTN_EDITNOTE = wx.NewId()
ID_BTN_DELETENOTE = wx.NewId()

ID_SPLIT_UNSPLIT = wx.NewId()

ID_TOOLS_NEW = wx.NewId()
ID_TOOLS_EDIT = wx.NewId()
ID_TOOLS_DELETE = wx.NewId()
ID_TOOLS_FILTER = wx.NewId()
ID_TOOLS_REFRESH = wx.NewId()
ID_TOOLS_OPTIONS = wx.NewId()
ID_TOOLS_SRCHBX = wx.NewId()
ID_TOOLS_FIND = wx.NewId()

snatcher_options = {}
myNotes = None
#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NoteSnatcher(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        main = MainFrame(None, -1, __title__)
        self.SetTopWindow(main)


class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(640, 480))
        global snatcher_options
        global myNotes

        # load options
        print("Loading options...")
        snatcher_options = load_options()
        if "ReopenNotebook" in snatcher_options and \
            snatcher_options["ReopenNotebook"]:
            if "LastNotebook" not in snatcher_options:
                print("There's a serious problem here.  "
                    "There is a problem with the options and especially "
                    "with the fact there's no last notebook.")
                sys.exit(1)
            print("Opening %s..." % (snatcher_options["LastNotebook"]))
            filename = snatcher_options["LastNotebook"]
            # if a last file exists, try to open it
            try:
                myNotes = snatcher.notebook(filename)
            except Exception as exc:
                logger.info("Exception (Opening previously used file.): "
                    "%s" % exc)
                logger.exception(exc)
                exit()
        else:
            print("Options:")
            print(snatcher_options)
            # don't specify a notes file to use
            try:
                myNotes = snatcher.notebook("new_notebook.db", create=True)
            except Exception as exc:
                logger.info("Exception (Creating new notes db.): %s" % exc)
                logger.exception(exc)
                exit()

        title = __title__ + " [" + os.path.split(myNotes.db)[1] + "]"
        self.SetTitle(title)

        self.splitter = wx.SplitterWindow(self, -1,
            style=wx.SP_PERMIT_UNSPLIT | wx.SP_3D)
        self.splitter.SetMinimumPaneSize(100)

        self.listpanel = wx.Panel(self.splitter, -1, style=wx.BORDER_SUNKEN)
        self.notepanel = wx.Panel(self.splitter, -1, style=wx.BORDER_SUNKEN)

        # do menu
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        filemenu.Append(ID_FILEMENU_NEW, "New notebook",
            "Create a new notebook.")
        filemenu.Append(ID_FILEMENU_OPEN, "Open notebook",
            "Open an existing notebook.")

        recentmenu = wx.Menu()
        self.recent_ids = {}
        if len(snatcher_options['RecentFiles']):
            for i in range(len(snatcher_options['RecentFiles'])):
                # don't include current notebook in list of recent files
                if snatcher_options['RecentFiles'][i] == myNotes.db:
                    continue
                recent_item = (wx.NewId(), snatcher_options['RecentFiles'][i])
                self.recent_ids[recent_item[0]] = recent_item[1]
                recentmenu.Append(recent_item[0], recent_item[1])
                self.Bind(wx.EVT_MENU, self.OpenRecent, id=recent_item[0])

        recentmenuid = wx.NewId()
        filemenu.AppendMenu(recentmenuid, "Recent files", recentmenu)
        if not len(snatcher_options['RecentFiles']):
            filemenu.Enable(recentmenuid, False)

        filemenu.AppendSeparator()
        filemenu.Append(ID_FILEMENU_IMPORT, 'Import...',
            'Import notes from another notebook.')
        filemenu.Append(ID_FILEMENU_EXPORT, 'Export...', 'Export notes.')
        filemenu.AppendSeparator()
        filemenu.Append(ID_FILEMENU_OPTIONS, 'Options...', 'Preferences.')
        filemenu.AppendSeparator()
        filemenu.Append(ID_FILEMENU_EXIT, 'E&xit\tCtrl+Q', 'Exit')
        notesmenu = wx.Menu()
        notesmenu.Append(ID_NOTESMENU_NEW, "New note", "Create a new note.")
        notesmenu.Append(ID_NOTESMENU_EDIT, "Edit note",
            "Edit the selected note.")
        notesmenu.Append(ID_NOTESMENU_DEL, "Delete note",
            "Delete the selected note.")
        notesmenu.AppendSeparator()
        notesmenu.Append(ID_NOTESMENU_VAC, "Vacuum notes",
            "Vacuum the notes database.")
        notesmenu.AppendSeparator()
        notesmenu.Append(ID_NOTESMENU_TRASH, "Show trash",
            "Show deleted notes.")
        notesmenu.Append(ID_NOTESMENU_EMPTYTRASH, "Empty trash",
            "Permanently remove deleted notes.")
        notesmenu.AppendSeparator()
        notesmenu.Append(ID_NOTESMENU_PROP, "Properties",
            "Notebook properties.")
        viewmenu = wx.Menu()
        self.shownote = viewmenu.Append(ID_VIEWMENU_SHOWHIDENOTE,
            "Show Note Preview\tCtrl+R", "Show the note preview.",
            kind=wx.ITEM_CHECK)
        self.shownote.Check(False)
        viewmenu.AppendSeparator()
        viewmenu.Append(ID_VIEWMENU_FILTER, "Filter by tags...",
            "Filter notes by tags.")
        viewmenu.Append(ID_VIEWMENU_SHOWALL, "Show all notes",
            "Reset filter and show all notes.")
        viewmenu.AppendSeparator()
        viewmenu.Append(ID_VIEWMENU_REFRESH, "Refresh Notes List\tF5",
            "Force a refresh of the notes list control.")
        viewmenu.AppendSeparator()
        self.showlistctrl = viewmenu.Append(ID_VIEWMENU_LISTCTRL,
            "Listctrl view", "Show notes as a list control.",
            kind=wx.ITEM_CHECK)
        self.showlistbox = viewmenu.Append(ID_VIEWMENU_LISTBOX,
            "Listbox view", "Show notes as a list control.",
            kind=wx.ITEM_CHECK)
        if snatcher_options["DisplayType"] == "listctrl":
            self.showlistctrl.Check(True)
        elif snatcher_options["DisplayType"] == "listbox":
            self.showlistbox.Check(True)
        menubar.Append(filemenu, "&File")
        menubar.Append(notesmenu, "N&otes")
        menubar.Append(viewmenu, "&View")
        self.SetMenuBar(menubar)

        # tool bar
        #toolbar = self.CreateToolBar()
        #icons = {'program':'snatcher.ico', 'new':'new.png',
             #'edit':'edit.png', 'delete':'delete.png',
             #'filter':'filter.png', 'refresh':'refresh.png',
             #'find':'find.png'}
        #icons = dict((k, os.path.join(icons_path, v)) for k, v in \
                #icons.items())
        # This is necessary so that it will be at the proper directory for
        # the relative links to the icons to work
        #if sys.platform == 'linux2':
            # not sure if this line is really necessary, test it out on linux
            #os.chdir(os.path.split(sys.argv[0])[0])
            #icons = dict((k, os.path.abspath(v)) for k,v in icons.items())
#        toolbar.AddSeparator()
#        toolbar.AddLabelTool(ID_TOOLS_NEW, "New", wx.Bitmap(icons['new']),
        #shortHelp="New note")
#        toolbar.AddLabelTool(ID_TOOLS_EDIT, "Edit", wx.Bitmap(icons['edit']),
#shortHelp="Edit note")
#        toolbar.AddLabelTool(ID_TOOLS_DELETE, "Delete",
# wx.Bitmap(icons['delete']), shortHelp="Delete note")
#        toolbar.AddSeparator()
#        toolbar.AddLabelTool(ID_TOOLS_FILTER, "Filter",
# wx.Bitmap(icons['filter']), shortHelp="Filter notes by tag")
#        toolbar.AddLabelTool(ID_TOOLS_REFRESH, "Refresh",
# wx.Bitmap(icons['refresh']), shortHelp="Refresh notes view")
#        toolbar.AddSeparator()
#        self.txtFind = wx.TextCtrl(toolbar, ID_TOOLS_SRCHBX,
# style= wx.TE_PROCESS_ENTER)
#        toolbar.AddControl(self.txtFind)
#        toolbar.AddLabelTool(ID_TOOLS_FIND, "Find",
# wx.Bitmap(icons['find']), shortHelp="Find")
#        toolbar.Realize()
#

        toolbar = self.CreateToolBar()
        toolbar.AddSeparator()
        toolbar.AddLabelTool(ID_TOOLS_NEW, "New",
            wx.Bitmap("icons/new.png"), shortHelp="New note")
        toolbar.AddLabelTool(ID_TOOLS_EDIT, "Edit",
            wx.Bitmap("icons/edit.png"), shortHelp="Edit note")
        toolbar.AddLabelTool(ID_TOOLS_DELETE, "Delete",
            wx.Bitmap("icons/delete.png"), shortHelp="Delete note")
        toolbar.AddSeparator()
        toolbar.AddLabelTool(ID_TOOLS_FILTER, "Filter",
            wx.Bitmap("icons/filter.png"), shortHelp="Filter notes by tag")
        toolbar.AddLabelTool(ID_TOOLS_REFRESH, "Refresh",
            wx.Bitmap("icons/refresh.png"), shortHelp="Refresh notes view")
        toolbar.AddSeparator()
        self.txtFind = wx.TextCtrl(toolbar, ID_TOOLS_SRCHBX,
            style=wx.TE_PROCESS_ENTER)
        toolbar.AddControl(self.txtFind)
        toolbar.AddLabelTool(ID_TOOLS_FIND, "Find",
            wx.Bitmap("icons/find.png"), shortHelp="Find")
        toolbar.Realize()

        # status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.Show()

        # systray icon
        icon = wx.EmptyIcon()
        try:
            icon.LoadFile("icons/snatcher.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)
            # set up task bar icon
            try:
                self.tbicon = TaskBarIcon(self, icon)
                self.tbicon.change_icon_text(title)
            except Exception as ex:
                logger.info("Exception creating taskbaricon: %s" % ex)
                logger.exception(ex)
                self.tbicon = None
        except:
            print("Icon can't be loaded.")
            self.tbicon = None

        # hide in systray on minimize
        # this should be an option
        if sys.platform == 'win32':
            self.hideOnMin = True
            #SortedListCtrl = SortedListCtrlWin
        else:
            print("sys.platform = %s" % sys.platform)
            self.hideOnMin = False

        # Widgets

        # TODO:  check options file for display type and order and set up
        # the proper widget accordingly
        self.display_type = snatcher_options["DisplayType"]
        self.display_order = None
        self.notes_list = None

        # TODO:  see if this should be in an if clause
        # might could leave them "on" all the time
        # but this might make htem drawn outside
        # of a sizer and just sitting there
        if self.display_type == "listctrl":
            # list control
            self.RebuildNotedict()
            #self.lstNotes.itemDataMap = self.notedict
            #self.lstNotes = SortedListCtrl(self.listpanel, self.notedict)
            #self.lstNotes = wx.ListCtrl(self.listpanel, size=(350, 300),
                #style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES |
                #wx.LC_VRULES)
            self.lstNotes = NewListCtrl(self.listpanel, self.notedict)
            self.lstNotes.InsertColumn(0, "Subject")
            self.lstNotes.InsertColumn(1, "Created")
            self.lstNotes.InsertColumn(2, "Edited")
            self.UpdateNotesList()
        elif self.display_type == "listbox":
            # list box
            self.display_type = "listbox"
            self.notes_list = wx.ListBox(self.listpanel, -1,
                size=(400, 300), style=wx.LB_SINGLE | wx.LB_HSCROLL)
            # listbox events
            self.Bind(wx.EVT_LISTBOX, self.on_listbox_item_selected,
                self.notes_list)
            self.Bind(wx.EVT_LISTBOX_DCLICK,
                self.on_listbox_item_doubleclicked, self.notes_list)

        #  note preview text control
        self.txtPreview = wx.TextCtrl(self.notepanel, -1,
            "Welcome to The Snatcher.", style=wx.TE_MULTILINE, size=(200, 150))

        vbox = wx.BoxSizer(wx.VERTICAL)
        if self.display_type == "listbox":
            vbox.Add(self.notes_list, 1, wx.ALL | wx.EXPAND |
                wx.ALIGN_CENTER_HORIZONTAL, 5)
        elif self.display_type == "listctrl":
            vbox.Add(self.lstNotes, 1, wx.ALL | wx.EXPAND |
            wx.ALIGN_CENTER_HORIZONTAL, 5)

        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox2.Add(self.txtPreview, 1, wx.ALL | wx.EXPAND, 5)

        # set up events
        # main form
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Bind(wx.EVT_ICONIZE, self.OnIconify)
        # controls
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListItemDoubleClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListItemSelected)
        # menu
        self.Bind(wx.EVT_MENU, self.OnNewNotebook, id=ID_FILEMENU_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpenNotebook, id=ID_FILEMENU_OPEN)
        self.Bind(wx.EVT_MENU, self.OnImport, id=ID_FILEMENU_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnExport, id=ID_FILEMENU_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnOptions, id=ID_FILEMENU_OPTIONS)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_FILEMENU_EXIT)
        self.Bind(wx.EVT_MENU, self.OnNewNote, id=ID_NOTESMENU_NEW)
        self.Bind(wx.EVT_MENU, self.OnEditNote, id=ID_NOTESMENU_EDIT)
        self.Bind(wx.EVT_MENU, self.OnDeleteNote, id=ID_NOTESMENU_DEL)
        self.Bind(wx.EVT_MENU, self.OnVacuum, id=ID_NOTESMENU_VAC)
        self.Bind(wx.EVT_MENU, self.OnNotesProperties, id=ID_NOTESMENU_PROP)
        self.Bind(wx.EVT_MENU, self.OnShowTrash, id=ID_NOTESMENU_TRASH)
        self.Bind(wx.EVT_MENU, self.OnEmptyTrash, id=ID_NOTESMENU_EMPTYTRASH)
        self.Bind(wx.EVT_MENU, self.OnShowNote, id=ID_VIEWMENU_SHOWHIDENOTE)
        self.Bind(wx.EVT_MENU, self.OnShowAll, id=ID_VIEWMENU_SHOWALL)
        self.Bind(wx.EVT_MENU, self.OnFilterByTags, id=ID_VIEWMENU_FILTER)
        self.Bind(wx.EVT_MENU, self.OnRefresh, id=ID_VIEWMENU_REFRESH)
        self.Bind(wx.EVT_MENU, self.OnShowListbox, id=ID_VIEWMENU_LISTBOX)
        self.Bind(wx.EVT_MENU, self.OnShowListctrl, id=ID_VIEWMENU_LISTCTRL)

        # toolbar buttons
        self.Bind(wx.EVT_TOOL, self.OnNewNote, id=ID_TOOLS_NEW)
        self.Bind(wx.EVT_TOOL, self.OnEditNote, id=ID_TOOLS_EDIT)
        self.Bind(wx.EVT_TOOL, self.OnDeleteNote, id=ID_TOOLS_DELETE)
        self.Bind(wx.EVT_TOOL, self.OnFilterByTags, id=ID_TOOLS_FILTER)
        self.Bind(wx.EVT_TOOL, self.OnRefresh, id=ID_TOOLS_REFRESH)
        #self.Bind(wx.EVT_TOOL, self.OnOptions, id=ID_TOOLS_OPTIONS)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnFind, id=ID_TOOLS_SRCHBX)
        self.Bind(wx.EVT_TOOL, self.OnFind, id=ID_TOOLS_FIND)

        self.Bind(wx.EVT_SPLITTER_UNSPLIT, self.OnUnsplit)
        #self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnUnsplit,
            #id=ID_SPLIT_UNSPLIT)
        #self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnUnsplit)

        if self.display_type == "listctrl":
            self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.lstNotes)

        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.ListContextMenu)

        self.listpanel.SetSizer(vbox)
        self.notepanel.SetSizer(vbox2)
        self.listpanel.SetFocus()

        self.splitter.SplitVertically(self.listpanel, self.notepanel)
        self.splitter.Unsplit()
        self.listpanel.SetFocus()

        self.SetClientSize(self.listpanel.GetBestSize())
        self.Centre()
        self.Show(True)

        #self.Layout()

        #self.selectedItem = -1
        # TODO:  see which one i'm still using
        # selected_note_id looks better
        self.selected_note_id = -1
        self.update_notes_display()

    def OnColClick(self, event):
        print "column clicked"
        event.Skip()

    def OnListItemSelected(self, e):
        """ Show a preview of the selected note in the preview box.
        This also rebuilds the notedict and updates the list control
        though it is probably overkill.  That shit should probably be
        done after the note has been saved and then instead of updating
        the entire thing the selected note should be updated. """
        print("Item Selected.")

        #~ selected = e.GetIndex()
        #~ lstCtrlDataItem = e.GetData()
        #~ print("getindex = %s" % (selected))
        #~ print("getdata = %s" % (lstCtrlDataItem))

        try:
            self.selectedItem = e.GetIndex()
            self.selectedItemKey = e.GetData()
            #self.RebuildNotedict()
            #self.lstNotes.itemDataMap = self.notedict
            nid = self.lstNotes.itemDataMap[e.GetData()][-1]
            print("e.GetData() = %s" % (e.GetData()))
            myNotes.select_note(nid)
            # should also get the note text and put it in the preview thingy
            self.txtPreview.Clear()
            #self.txtPreview.WriteText(unicode(myNotes.currentNote))
            self.txtPreview.WriteText(myNotes.currentNote.notedata)
            self.txtPreview.ShowPosition(0)
        except Exception as exc:
            logger.info("EXCEPTION (OnListItemSelected): %s" % exc)
            logger.exception(exc)
            return
        print("the end")

    def OnListItemDoubleClick(self, e):
        """ Double-click handler for list control that brings up the edit
        dialog for the selected note. """
        print("Item double-clicked.")
        try:
            # get the last value from the selected key which is a
            # hidden value containing the id
            #print(e.GetData())
            #id = self.lstNotes.itemDataMap[e.GetData()][-1]
            myNotes.select_note(myNotes.currentNote.noteid)
            self.EditNote(True)
        except Exception as exc:
            logger.info("EXCEPTION (OnListItemDoubleClick): %s" % exc)
            logger.exception(exc)
            return

    def UpdateNotesList(self):
        """ Clear the notes list control and rebuild it with a current
        list of all of the items. """
        if self.lstNotes.GetItemCount() > 0:
            self.lstNotes.DeleteAllItems()
        #self.RebuildNotedict()

        # not sure wtf this does but it's necessary
        #self.lstNotes.SetColumnCount(len(self.notedict))
        items = self.notedict.items()
        index = 0
        print "items len:  ", len(items)
        print("Adding items to list control...")
        for k, v in items:
            #print("Item:")
            #print(v)
            index = self.lstNotes.InsertStringItem(index, v[0])
            self.lstNotes.SetStringItem(index, 1, v[1])
            self.lstNotes.SetStringItem(index, 2, v[2])
            # this maps the line in the list ctrl to the item in the data dict
            self.lstNotes.SetItemData(index, k)
            #print("added")
        # set the column widths
        self.lstNotes.SetColumnWidth(0, 150)
        self.lstNotes.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.lstNotes.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)

        # update status bar
        self.UpdateStatusBar("Showing %d out of %d notes." % (len(items),
            myNotes.count()))

    def UpdateListMapping(self):
        self.RebuildNotedict()
        self.lstNotes.itemDataMap = self.notedict
        self.lstNotes.SetColumnCount(len(self.notedict))
        items = self.notedict.items()
        index = 0
        print("Updating mapping on list control...")
        for k, v in items:
            # this maps the line in the list ctrl to the item in the data dict
            self.lstNotes.SetItemData(index, k)
            index += 1

    def RebuildNotedict(self):
        """ This will recreate the dict that contains all of the notes
        for the list control. """
        self.allnotes = myNotes.get_preview_items()
        self.notedict = {i: (n.subject, n.crtime, n.mtime, n.noteid)
            for i, n in enumerate(self.allnotes)}

    def OnCloseWindow(self, event):
        """ Exit the program. """
        if self.tbicon is not None:
            self.tbicon.Destroy()
        self.Destroy()

    def OnExit(self, e):
        """ Exit the program. """
        snatcher_options["LastNotebook"] = myNotes.db
        print("Saving %s as last file..." % myNotes.db)
        try:
            save_options(od=snatcher_options)
        except Exception as exc:
            logger.info("Exception in OnExit: " + str(exc))
            logger.exception(exc)
        if self.tbicon is not None:
            self.tbicon.Destroy()
        self.Destroy()

    def OnNewNotebook(self, e):
        dlg = wx.FileDialog(self, message="Save new Snatcher notebook as:",
            defaultDir=os.getcwd(), defaultFile="notes.db",
            wildcard="SQLite database (*.db)|*.db",
            style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            print("Filename = ", filename)
            global myNotes
            myNotes = snatcher.notebook(filename, create=True)
            self.open_file(myNotes.db)
        dlg.Destroy()

    def OnOpenNotebook(self, e):
        dlg = wx.FileDialog(self, message="Select Snatcher notebook to open:",
            defaultDir=os.getcwd(), defaultFile="",
            wildcard="SQLite database (*.db)|*.db", style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            print("Filename = ")
            print(filename)
            self.open_file(filename)
        dlg.Destroy()

    def open_file(self, filename):
        global myNotes
        previous_notebook = myNotes.db
        # add current (soon to be previous) notebook into recent list
        if previous_notebook not in snatcher_options['RecentFiles']:
            pass
            recent_item = (wx.NewId(), previous_notebook)
            self.recent_ids[recent_item[0]] = recent_item[1]
            #recentmenu.
            """What I'm trying to do here is to make a menu item for the
            previous notebook so that it can be added to the top of the
            recent list in the menu.  This way if the user has opened a
            notebook and then they want to go back to the previous one,
            they can just look in the recent menu and reload it.
            Not sure if I'm going to have to totally recreate the recent
            menu or what.  Maybe get the current items, then one by one
            go through and add them again but this time starting with the
            most recent (previous_notebook), and then added the other items
            making sure not to add the notebook that was just added.
            Or maybe I can have a member variable pointing to the
            recent menu and modify it by just removing the current
            notebook (if necessary) and then adding the previous notebook
            to the top (and removing it beforehand if it was already there)."""
        myNotes = snatcher.notebook(filename)
        self.RefreshNotesList()
        # if filename is already in the recent files, delete it,
        # then it gets re-added, hopefully this is one way to prevent
        # duplicate files from appearing in the list
        if filename in snatcher_options['RecentFiles']:
            snatcher_options['RecentFiles'].remove(filename)
        snatcher_options['RecentFiles'].insert(0, filename)
        print("A new file has been opened.")
        print("Recent files now looks like this:  ")
        print(str(snatcher_options['RecentFiles']))
        title = __title__ + " [" + os.path.split(myNotes.db)[1] + "]"
        self.SetTitle(title)
        self.tbicon.change_icon_text(title)

    def OpenRecent(self, e):
        self.open_file(self.recent_ids[e.GetId()])

    def OnNewNote(self, e):
        """ Create a new note. """
        # open new note dialog
        print("Create a new note.")
        myNotes.currentNote = snatcher.note()
        self.EditNote(False)

    def OnEditNote(self, e):
        """ Edit the selected note. """
        print("Edit selected note.")

        if self.display_type == "listbox":
            # make sure something is selected
            if not self.notes_list.GetSelections():
                return
        elif self.display_type == "listctrl":
            # make sure there is at least one note to edit
            if myNotes.count() < 1:
                print("Note count is < 1.")
                return
            # make sure something is selected in the control
            if not self.lstNotes.GetSelectedItemCount():
                print("Nothing selected.")
                return
        myNotes.select_note(myNotes.currentNote.noteid)
        self.EditNote(True)

    def EditNote(self, edit):
        """ Edit note. """
        if myNotes.currentNote:
            print("editing note:  %d" % (myNotes.currentNote.noteid))
        n = myNotes.get_temp_note(myNotes.currentNote.noteid)
        if n:
            # ask if user wants to restore auto-saved notes
            box = wx.MessageDialog(self, "Auto-saved note found.  "
                "Do you want to restore it?\nPreview:\n\nSubject:  "
                "%s\nTags:  %s\nContent:  %s" % (n.subject,
                n.tagstring, n.notedata[:80]),
                "Auto-saved note detected",
                wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if box.ShowModal() == wx.ID_NO:
                print("not restoring")
                if not edit:
                    # set current note to a new note
                    myNotes.currentNote = snatcher.note()
            else:
                print("restoring auto-saved note")
                myNotes.currentNote.subject = n.subject
                myNotes.currentNote.tagstring = n.tagstring
                myNotes.currentNote.notedata = n.notedata
            myNotes.delete_temp_note(myNotes.currentNote.noteid, True)

        if edit:
            editnote = EditNoteFrame(self, -1, "Edit Note", myNotes,
                myNotes.currentNote.noteid)
            #editnote.ShowNote()
        else:
            editnote = EditNoteFrame(self, -1, "New Note", myNotes)
            #editnote.ShowNote()
        editnote.Centre()

        val = editnote.ShowModal()
        if val == wx.ID_OK:
            n = editnote.get_note_fields()
            s = editnote.txtTags.GetValue()
            if edit:
                #print("id = %d" % ())
                n.noteid = myNotes.currentNote.noteid
                print("id = %d" % myNotes.currentNote.noteid)
                myNotes.update_note(n)
                myNotes.update_tags(s)
                myNotes.select_note(n.noteid)
            else:
                myNotes.add_note(n)
                myNotes.select_new_note()
                myNotes.update_tags(s)
                myNotes.select_new_note()
            n = myNotes.currentNote
            #self.UpdateNotesList()
            # delete temporary note if there is one
            if editnote.temp_id:
                print("temp note found, about to delete...")
                myNotes.delete_temp_note(editnote.temp_id)
            else:
                print("no temp note???")

            # TODO:  make this more generic so as to update whichever
            # widget is currently showing the notes

            if self.display_type == "listbox":
                self.update_notes_display()
            elif self.display_type == "listctrl":
                if edit:
                    # update the selected note
                    self.lstNotes.SetStringItem(self.selectedItem, 0,
                        n.subject)
                    self.lstNotes.SetStringItem(self.selectedItem, 2, n.mtime)
                else:
                    # insert a new item intro list ctrl and get its index
                    index = self.lstNotes.InsertStringItem(sys.maxint,
                        n.subject)
                    self.lstNotes.SetStringItem(index, 1, n.crtime)
                    self.lstNotes.SetStringItem(index, 2, n.mtime)

                    dl = self.lstNotes.itemDataMap.keys()
                    dl.sort()
                    print("dl = %s" % dl)

                    # this associates the item in the list ctrl with an item
                    # in the control's dict
                    # check the length in case there are no notes already
                    if len(dl):
                        print("TRUE dl len = %d" % (len(dl)))
                        self.lstNotes.SetItemData(index, dl[-1] + 1)
                    else:
                        print("FALSE dl len = %d" % (len(dl)))
                        self.lstNotes.SetItemData(index, 1)
                # update item data
                self.RebuildNotedict()
                self.lstNotes.SetColumnCount(len(self.notedict))
                self.lstNotes.itemDataMap = self.notedict
                #print(self.lstNotes.itemDataMap[self.selectedItem])
                #self.lstNotes.itemDataMap[self.selectedItem][0] = "HONK!"
                #self.lstNotes.RefreshItem(
                # SetItem(long index, int col, const wxString& label,
                #int imageId = -1)
                #self.lstNotes.SetItem(self.selectedItem,
                    # "This note was edited")
                self.UpdateStatusBar("Showing %d out of %d notes." %
                    (len(self.lstNotes.itemDataMap), myNotes.count()))
                # TESTING
                dl = self.lstNotes.itemDataMap.keys()
                dl.sort()
                print("dl = %s" % dl)
        editnote.Destroy()

    def OnDeleteNote(self, e):
        """ Delete the selected note. """
        print("in delete note")
        self.DeleteNote()

    def DeleteNote(self):
        """Delete note"""

        # TODO:  make this work with whichever widget is showing the notes

        # make sure something is selected in the control
        if self.display_type == "listbox":
            if not self.notes_list.GetSelections():
                print("Nothing selected.")
                return
        elif self.display_type == "listctrl":
            if not self.lstNotes.GetSelectedItemCount():
                print("Nothing selected.")
                return

        #show confirmation message box
        if snatcher_options["ConfirmDelete"]:
            box = wx.MessageDialog(self,
                "Are you sure you want to delete this note?",
                "Warning:  R U SURE LOL",
                wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if box.ShowModal() == wx.ID_NO:
                return
        myNotes.delete_note(myNotes.currentNote.noteid)

        if self.display_type == "listbox":
            # TODO:
            pass
        elif self.display_type == "listctrl":
            # TESTING
            dl = self.lstNotes.itemDataMap.keys()
            dl.sort()
            print("dl = %s" % dl)
            # this should probably just remove that particular note item
            # from the list instead of updating the entire thing
            # should remove that item
            self.lstNotes.DeleteItem(self.selectedItem)
            # does the list control's data need to be updated as well or
            # does the DeleteItem method take care of that?
            del self.lstNotes.itemDataMap[self.selectedItemKey]
            self.UpdateListMapping()
            # update item data
            #~ self.RebuildNotedict()
            #~ self.lstNotes.SetColumnCount(len(self.notedict))
            #~ self.lstNotes.itemDataMap = self.notedict
            # TESTING
            dl = self.lstNotes.itemDataMap.keys()
            dl.sort()
            print("dl = %s" % dl)

            self.UpdateStatusBar("Showing %d out of %d notes." %
                (len(self.lstNotes.itemDataMap), myNotes.count()))

    def OnVacuum(self, e):
        """ Vacuum the notes database. """
        myNotes.vacuum()

    def OnNotesProperties(self, e):
        """Show notebook properties."""
        # TODO show full path of notebook not just the value of NOTEBOOK.db
        # currently shows full path in win32
        msg = "Notebook path:\n%s\n\nNumber of notes: %d\n" % \
            (myNotes.db, myNotes.count())
        msg += "\n%s (C) 2015 %s" % (__title__, __author__)
        #msg += "\nCurrent working directory:  %s" % (os.getcwd())
        #msg += "\nsys.argv = %r" % sys.argv
        box = wx.MessageDialog(self, msg, "Notebook properties",
            wx.ICON_INFORMATION)
        box.ShowModal()

    def OnShowTrash(self, e):
        """View deleted notes."""
        print("Showing trash.")
        try:
            trash = TrashFrame(self, -1, "Deleted notes", myNotes)
            trash.Show()
        except Exception as exc:
            box = wx.MessageDialog(self, str(exc),
               "Error showing trash frame", wx.ICON_EXCLAMATION)
            logger.exception(exc)
            box.ShowModal()

    def OnEmptyTrash(self, e):
        """Empty the trash."""
        # delete the deleted notes
        #TODO:  show a confirmation
        myNotes.empty_trash()
        msg = "Trash emptied."
        box = wx.MessageDialog(self, msg, "", wx.ICON_INFORMATION)
        box.ShowModal()

    def OnIconify(self, e):
        """ Hide the main window on minimization leaving the icon
        in the systray. """
        if self.hideOnMin:
            if self.tbicon is not None:
                self.Hide()

    def OnImport(self, e):
        """ Import the notes from selected format. """
        # need to have a file picker here
        dlg = wx.FileDialog(self, message="Choose a file to import",
            defaultDir=os.getcwd(), defaultFile="",
            wildcard="Note Snatcher XML (*.xml)|*.xml",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            print("Filename = ")
            print(filename)
            idx = dlg.GetFilterIndex()
            print("Index = %d" % idx)
            import_types = ("xml")
            myNotes.import_notes(filename, import_types[idx])
            self.RefreshNotesList()
        dlg.Destroy()
        #box = wx.MessageDialog(self, "Notes loaded from file %s."
        # % filename, "File loaded.", wx.OK)
        #box.ShowModal()

    def OnExport(self, e):
        """ Export the notes to selected format. """
        dlg = wx.FileDialog(self, message="Export file",
            defaultDir=os.getcwd(), defaultFile=myNotes.db + ".xml",
            wildcard="Note Snatcher XML (*.xml)|*.xml|HTML (*.htm)|*.htm"
            "|UTF-8 Text (*.txt)|*.txt",
            style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            print("Filename = ")
            print(filename)
            idx = dlg.GetFilterIndex()
            print("Index = %d" % idx)
            # check for proper extension and add it if necessary
            #filename = filename.replace("\\", "\\\\")
            export_types = ("xml", "html", "txt")
            myNotes.export_notes(filename, export_types[idx])
        dlg.Destroy()

        #box = wx.MessageDialog(self, "Notes backed up to file %s."
        # % filename, "File saved.", wx.OK)
        #box.ShowModal()

    def OnOptions(self, e):
        """Show options."""
        try:
            optionsframe = OptionsFrame(self, -1, "Options",
                od=snatcher_options)
            print("about to show options")
            if optionsframe.ShowModal() == wx.ID_OK:
                print("options saved")
                snatcher_options['ReopenNotebook'] = \
                    optionsframe.reopen_last.GetValue()
                #snatcher_options['RememberNotebooks'] = \
                    #optionsframe.remember_notebooks.GetValue()
                #snatcher_options['NumberOfNotebooks'] = \
                    #optionsframe.previous_notebooks_count.GetValue()
                snatcher_options['ConfirmDelete'] = \
                    optionsframe.confirm_delete.GetValue()
                snatcher_options['SaveDeleted'] = \
                    optionsframe.use_trash.GetValue()
                snatcher_options['DefaultSortOrder'] = \
                    optionsframe.default_sort.GetValue()
                snatcher_options['MinimizeToTray'] = \
                    optionsframe.min_systray.GetValue()
                snatcher_options['CloseToTray'] = \
                    optionsframe.close_systray.GetValue()
            else:
                print("options cancelled")

        except Exception as exc:
            box = wx.MessageDialog(self, exc.message, "Error",
                wx.ICON_EXCLAMATION)
            logger.exception(exc)
            box.ShowModal()

    def OnUnsplit(self, e):
        """ When the splitter is unsplit, make sure the menu changes """
        self.shownote.Check(False)
        #box = wx.MessageDialog(self, "Splitter unsplit", "", wx.OK)
        #box.ShowModal()



    def OnShowListctrl(self, e):
        print "show list ctrl event"
        # seems to be a problem because it checks it BEFORE it sees if it's
        # checked and this makes the IsChecked check fail
        if self.showlistbox.IsChecked():
            # check listctrl
            self.showlistctrl.Check(True)
            # uncheck  listbox
            self.showlistbox.Check(False)
            self.ChangeView("listctrl")

    def OnShowListbox(self, e):
        print "show list box event"
        if self.showlistctrl.IsChecked():
            # uncheck listbox
            self.showlistbox.Check(True)
            # check  listctrl
            self.showlistctrl.Check(False)
            self.ChangeView("listbox")

    def ChangeView(self, t="listctrl"):
        print "inside of changeview()"
        if t == "listctrl":
            # change to listctrl
            print "changing to listctrl"
        elif t == "listbox":
            # change to listbox
            print "changing to listbox"
        else:
            print "WTF?  this is no type of view yet:  %s" % (t)
        # change options
        snatcher_options["DisplayType"] = t
        # show message box about view won't change until you restart
        box = wx.MessageDialog(self, "Restart to change view type to %s." %
            (t), "Changing view type", wx.ICON_INFORMATION)
        box.ShowModal()


    def OnShowNote(self, e):
        """ Show or hide the note panel. """
        if self.shownote.IsChecked():
            self.splitter.SplitHorizontally(self.listpanel, self.notepanel)
            self.listpanel.SetFocus()
            #self.notepanel.Show()
        else:
            self.splitter.Unsplit()
            self.listpanel.SetFocus()
            #self.notepanel.Hide()

    def ShowNote(self, show):
        if show:
            self.splitter.SplitHorizontally(self.listpanel, self.notepanel)
            self.listpanel.SetFocus()
            self.shownote.Check(True)
        else:
            self.splitter.Unsplit()
            self.listpanel.SetFocus()
            self.shownote.Check(False)

    def OnRefresh(self, e):
        #self.RefreshNotesList()
        self.update_notes_display()

    def RefreshNotesList(self):
        """ Refresh the view manually. """
        self.txtFind.Clear()
        myNotes.tags = []
        if self.display_type == "listctrl":
            self.RebuildNotedict()
            self.lstNotes.itemDataMap = self.notedict
            self.UpdateNotesList()
        elif self.display_type == "listbox":
            # TODO
            pass

    def OnShowAll(self, e):
        """ Clear tag filters and show all notes. """
        # which is better, comparison with [] or checking the list len?
        # if len(myNotes.tags) > 0:
        if myNotes.tags:
            myNotes.tags = []

            # TODO:  make this work with whichever widget is showing the notes
            if self.display_type == "listbox":
                pass
                # TODO
            elif self.display_type == "listctrl":
                self.RebuildNotedict()
                self.lstNotes.itemDataMap = self.notedict
                self.UpdateNotesList()

    def OnFilterByTags(self, e):
        """ Show edit tags dialog so that tag filters can be selected. """
        oldtags = myNotes.tags
        edittags = EditTagsFrame(self, -1, "Edit Tags", "notelist", myNotes)
        edittags.Centre()
        val = edittags.ShowModal()
        if val == wx.ID_OK:
            # TODO:  make this work with whichever widget is showing the notes

            if self.display_type == "listbox":
                results = myNotes.get_preview_items()
                self.current_notes = [i.subject for i in results]
                self.current_ids = [i.noteid for i in results]
                self.add_notes_to_listbox()
            elif self.display_type == "listctrl":
                self.RebuildNotedict()
                self.lstNotes.itemDataMap = self.notedict
                self.UpdateNotesList()
        else:
            # restore old tags
            myNotes.tags = oldtags[:]
        edittags.Destroy()

    def UpdateStatusBar(self, msg):
        """ Update the status bar text. """
        self.statusbar.SetStatusText(msg)

    def OnFind(self, e):
        q = self.txtFind.GetValue()
        if q == "":
            print("Enter a search query!")
            return

        results = myNotes.find(q)
        if len(results) < 1:
            # TODO:  should this be if not results?
            print("Nothing found.")
            return

        # TODO:  need to add the results to whatever widget is currently
        # showing them

        if self.display_type == "listbox":
            self.current_notes = [i[0] for i in results]
            self.current_ids = [i[-1] for i in results]
            self.add_notes_to_listbox()
        elif self.display_type == "listctrl":
            self.allnotes = results
            self.notedict = {}
            place = 1
            print("Rebuilding notes...")
            for n in self.allnotes:
                self.notedict[place] = (n.subject, n.crtime, n.mtime, n.noteid)
                place += 1
            #self.RebuildNotedict()
            self.lstNotes.itemDataMap = self.notedict
            self.UpdateNotesList()

    def ListContextMenu(self, e):
        cpos = self.GetClientAreaOrigin()
        pos = e.GetPosition()

        x = cpos[0] + pos[0] + 10
        y = cpos[1] + pos[1] + 10

        print("Showing context menu")
        self.PopupMenu(NoteContext(self), (x, y))

    def on_listbox_item_selected(self, e):
        """ Change currently selected note id to the one that was just
        selected on the listbox."""
        self.selected_note_id = self.current_ids[e.GetSelection()]
        myNotes.select_note(self.selected_note_id)
        print("Item selected.")

    def on_listbox_item_doubleclicked(self, e):
        """Edit note when it's double-clicked in listbox."""
        self.EditNote(True)

    def update_notes_display(self):
        """Generic notes display method that will automatically pick the
        right widget to update."""
        if self.display_type == "listbox":
            all_notes = myNotes.get_note_subjects()
            #self.current_notes = [i[1] for i in all_notes]
            self.current_notes = [i.subject for i in all_notes]
            #self.current_ids = [i[0] for i in all_notes]
            self.current_ids = [i.noteid for i in all_notes]
            self.add_notes_to_listbox()
        elif self.display_type == "listctrl":
            self.add_notes_to_listctrl()

    def add_notes_to_listbox(self):
        """Add notes to listbox."""
        self.notes_list.Clear()
        self.notes_list.InsertItems(self.current_notes, 0)

    def add_notes_to_listctrl(self):
        """Add notes to listctrl."""
        # TODO
        # Take the code from self.UpdateNotesList() and just put it here
        self.UpdateNotesList()


class TaskBarIcon(wx.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE = wx.NewId()

    def __init__(self, frame, icon):
        self.icon = icon
        wx.TaskBarIcon.__init__(self)
        self.SetIcon(icon, __title__)
        self.frame = frame

        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "&Restore")
        menu.Append(self.TBMENU_CLOSE,   "E&xit")
        return menu

    def OnTaskBarActivate(self, e):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
            #self.frame.RequestUserAttention()
        if not self.frame.IsShown():
            self.frame.Show(True)
            self.frame.Raise()

    def OnTaskBarClose(self, e):
        wx.CallAfter(self.frame.Close)

    def change_icon_text(self, t):
        """Change the icon text"""
        self.SetIcon(self.icon, str(t))

if sys.platform == 'win32':
    class NewListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.ColumnSorterMixin,
            ListRowHighlighter):
        def __init__(self, parent, noteitems):
            wx.ListCtrl.__init__(self, parent, -1,
                style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES |
                wx.LC_VRULES, size=(400, 300))
            wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self, 3)
            # TODO
            # make this an option as it significantly slows down refreshing
            #ListRowHighlighter.__init__(self)
            self.itemDataMap = noteitems

        def GetListCtrl(self):
            return self
else:
    class NewListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.ColumnSorterMixin):
        def __init__(self, parent, noteitems):
            wx.ListCtrl.__init__(self, parent, -1,
                style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES |
                wx.LC_VRULES, size=(400, 300))
            wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self, 3)
            self.itemDataMap = noteitems

        def GetListCtrl(self):
            return self


class NoteContext(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        # edit
        edit = wx.MenuItem(self, wx.NewId(), 'Edit')
        self.AppendItem(edit)
        # show preview
        self.preview = wx.MenuItem(self, wx.NewId(), 'Show Note',
            kind=wx.ITEM_CHECK)
        self.AppendItem(self.preview)
        if self.parent.shownote.IsChecked():
            self.preview.Check(True)
        else:
            self.preview.Check(False)
        # separator
        self.AppendSeparator()
        # delete
        delete = wx.MenuItem(self, wx.NewId(), 'Delete')
        self.AppendItem(delete)

        self.Bind(wx.EVT_MENU, self.OnEdit, edit)
        self.Bind(wx.EVT_MENU, self.OnShowPreview, self.preview)
        self.Bind(wx.EVT_MENU, self.OnDelete, delete)

    def OnEdit(self, e):
        print("Context menu: edit")
        self.parent.EditNote(True)

    def OnShowPreview(self, e):
        print("Context menu: preview")
        if self.preview.IsChecked():
            print("It was hidden, now show it")
            self.parent.ShowNote(True)
        else:
            print("It was checked, now hide it")
            self.parent.ShowNote(False)

    def OnDelete(self, e):
        pass
        print("Context menu: delete")
        self.parent.DeleteNote()


def save_options(od, filename='snatcher.ini'):
    """Save changed options to the disk."""
    print "save options was called"
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    if isinstance(snatcher_options, dict):
        config.add_section('Snatcher Settings')
        config.set('Snatcher Settings', 'ReopenNotebook',
            snatcher_options['ReopenNotebook'])
        #config.set('Snatcher Settings', 'RememberNotebooks',
            #snatcher_options['RememberNotebooks'])
        #config.set('Snatcher Settings', 'NumberOfNotebooks',
            #snatcher_options['NumberOfNotebooks'])
        config.set('Snatcher Settings', 'ConfirmDelete',
            snatcher_options['ConfirmDelete'])
        config.set('Snatcher Settings', 'SaveDeleted',
            snatcher_options['SaveDeleted'])
        config.set('Snatcher Settings', 'DefaultSortOrder',
            snatcher_options['DefaultSortOrder'])
        config.set('Snatcher Settings', 'DisplayType',
            snatcher_options['DisplayType'])
        config.set('Snatcher Settings', 'MinimizeToTray',
            snatcher_options['MinimizeToTray'])
        config.set('Snatcher Settings', 'CloseToTray',
            snatcher_options['CloseToTray'])
        config.set('Snatcher Settings', 'LastNotebook',
            snatcher_options['LastNotebook'])
        config.add_section('Recent')
        config.set('Recent', 'Count', snatcher_options['RecentCount'])

        print("Length of recent files to remember:  ")
        print(snatcher_options['RecentCount'])
        print("Number of recent files currently stored:  ")
        print(len(snatcher_options['RecentFiles']))

        if snatcher_options['RecentCount']:
            for i in range(snatcher_options['RecentCount']):
                print("i = %d" % (i))
                if i + 1 > len(snatcher_options['RecentFiles']):
                    break
                config.set('Recent', 'recent' + str(i + 1),
                    snatcher_options['RecentFiles'][i])
    with open(filename, 'wb') as configfile:
        config.write(configfile)


def load_options(filename='snatcher.ini'):
    """Load currently saved options from the disk."""
    import ConfigParser

    print "load options was called"
    # set some defaults
    options = {}
    options['ReopenNotebook'] = True
    #options['RememberNotebooks'] = True
    #options['NumberOfNotebooks'] = 5
    options['LastNotebook'] = ''
    options['ConfirmDelete'] = False
    options['SaveDeleted'] = True
    options['DefaultSortOrder'] = 'Created Ascending'
    options['DisplayType'] = 'listctrl'
    options['MinimizeToTray'] = True
    options['CloseToTray'] = False
    options['RecentCount'] = 5
    options['RecentFiles'] = []

    if os.path.exists(filename):
        config = ConfigParser.RawConfigParser()
        config.read(filename)
        try:
            # save to options dict
            options['ReopenNotebook'] = config.getboolean('Snatcher Settings',
                'ReopenNotebook')
            #options['RememberNotebooks'] =
                #config.getboolean('Snatcher Settings',
                #'RememberNotebooks')
            #options['NumberOfNotebooks'] = config.getint('Snatcher Settings',
                #'NumberOfNotebooks')
            options['LastNotebook'] = config.get('Snatcher Settings',
                'LastNotebook')
            options['ConfirmDelete'] = config.getboolean('Snatcher Settings',
                'ConfirmDelete')
            options['SaveDeleted'] = config.getboolean('Snatcher Settings',
                'SaveDeleted')
            options['DefaultSortOrder'] = config.get('Snatcher Settings',
                'DefaultSortOrder')
            options['DisplayType'] = config.get('Snatcher Settings',
                'DisplayType')
            options['MinimizeToTray'] = config.getboolean('Snatcher Settings',
                'MinimizeToTray')
            options['CloseToTray'] = config.getboolean('Snatcher Settings',
                'CloseToTray')
            options['RecentCount'] = int(config.get('Recent', 'Count'))
            if options['RecentCount']:
                options['RecentFiles'] = []
            try:
                for i in range(options['RecentCount']):
                    print(i)
                    if config.has_option("Recent", 'recent' + str(i + 1)):
                        rf = config.get('Recent', 'recent' + str(i + 1))
                        options['RecentFiles'].append(rf)
                        recentf = 'recent' + str(i + 1)
                    else:
                        break
                    logger.info(recentf)
                    logger.info(options['RecentFiles'][i])
            except Exception as exc:
                logger.exception(exc)

        except Exception as exc:
            logger.info("Problem loading options\n" + exc.message)
            logger.exception(exc)
    return options

if __name__ == "__main__":
    app = NoteSnatcher()
    app.MainLoop()
