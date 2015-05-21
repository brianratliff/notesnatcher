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


class OptionsFrame(wx.Dialog):

    options = {}

    def __init__(self, parent, id, title, od=None):
        wx.Dialog.__init__(self, parent, id, "Options", size=(450, 400),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.options = od

        panel = wx.Panel(self, -1, style=wx.BORDER_SUNKEN)

        # widgets
        #loading_group = wx.StaticBox(panel, -1, "Loading")
        notebook_group = wx.StaticBox(panel, -1, "Notebook")
        appearance_group = wx.StaticBox(panel, -1, "Appearance")

        self.reopen_last = wx.CheckBox(panel, -1,
            "Automatically reopen the last notebook used.")
        #self.remember_notebooks = wx.CheckBox(panel, -1,
            #"Remember previously used notebooks.")
        #self.previous_notebooks_label = wx.StaticText(panel, -1,
            #"Number of previously used notebooks to remember:")
        #self.previous_notebooks_count = wx.SpinCtrl(panel, -1, min=0,
            #initial=5, max=50)
        self.confirm_delete = wx.CheckBox(panel, -1,
            "Show delete confirmation when deleting a note.")
        self.use_trash = wx.CheckBox(panel, -1, "Keep deleted notes in trash.")

        self.sort_label = wx.StaticText(panel, -1, "Default sort order:")
        sort_choices = ["Created Ascending", "Created Descending",
            "Edited Ascending", "Edited Descending", "Subject Ascending",
            "Subject Descending"]
        self.default_sort = wx.ComboBox(panel, -1, "Created Ascending",
            choices=sort_choices, style=wx.CB_READONLY)

        self.min_systray = wx.CheckBox(panel, -1, "Minimize to systray"
            "(notification area).")
        self.close_systray = wx.CheckBox(panel, -1, "Close to systray"
            "(notification area).")

        btnOkay = wx.Button(panel, wx.ID_OK, "Save")
        btnCancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")

        # sizers
        vbox = wx.BoxSizer(wx.VERTICAL)

        #loading_sizer = wx.StaticBoxSizer(loading_group, wx.VERTICAL)
        notebook_sizer = wx.StaticBoxSizer(notebook_group, wx.VERTICAL)
        appearance_sizer = wx.StaticBoxSizer(appearance_group, wx.VERTICAL)

        #loading_sizer.Add(self.reopen_last, 0, wx.ALL, 5)
        #loading_sizer.Add(self.remember_notebooks, 0, wx.ALL, 5)

        #hbox_oldnotes = wx.BoxSizer(wx.HORIZONTAL)
        #hbox_oldnotes.Add(self.previous_notebooks_label, 0, wx.ALL, 5)
        #hbox_oldnotes.Add(self.previous_notebooks_count, 0, wx.ALL, 5)
        #loading_sizer.Add(hbox_oldnotes, 0, wx.ALL, 5)

        notebook_sizer.Add(self.reopen_last, 0, wx.ALL, 5)
        notebook_sizer.Add(self.confirm_delete, 0, wx.ALL, 5)
        notebook_sizer.Add(self.use_trash, 0, wx.ALL, 5)

        hbox_sorting = wx.BoxSizer(wx.HORIZONTAL)
        hbox_sorting.Add(self.sort_label, 0, wx.ALL, 5)
        hbox_sorting.Add(self.default_sort, 0, wx.ALL, 5)
        appearance_sizer.Add(hbox_sorting, 0, wx.ALL, 5)

        appearance_sizer.Add(self.min_systray, 0, wx.ALL, 5)
        appearance_sizer.Add(self.close_systray, 0, wx.ALL, 5)

        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(btnOkay, 0, wx.ALL, 5)
        btnbox.Add(btnCancel, 0, wx.ALL, 5)

        #vbox.Add(loading_sizer, 0, wx.ALL, 5)
        vbox.Add(notebook_sizer, 0, wx.ALL, 5)
        vbox.Add(appearance_sizer, 0, wx.ALL, 5)
        vbox.Add(btnbox, 0, wx.ALIGN_CENTRE | wx.ALIGN_BOTTOM)

        panel.SetSizer(vbox)

        self.set_options()

        self.Centre()
        self.Show(True)
        self.SetClientSize(panel.GetBestSize())

    def set_options(self):
        """Get options and set up the widgets."""
        # set values in widgets
        self.reopen_last.SetValue(self.options['ReopenNotebook'])
        #self.remember_notebooks.SetValue(self.options['RememberNotebooks'])
        #self.previous_notebooks_count.SetValue(self.options[ 'NumberOf' \
            #'Notebooks'])
        self.confirm_delete.SetValue(self.options['ConfirmDelete'])
        self.use_trash.SetValue(self.options['SaveDeleted'])
        self.default_sort.SetValue(self.options['DefaultSortOrder'])
        self.min_systray.SetValue(self.options['MinimizeToTray'])
        self.close_systray.SetValue(self.options['CloseToTray'])
