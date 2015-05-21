# Note Snatcher #

## Overview ##

Note Snatcher is a notes application written using Python and utilizing a SQLite database.  The program keeps track of notes and allows the user to view the different notes by date, subject, or with tags.  Because having lots of notes will make it hard to find certain ones, the user is able to filter/find the notes by the tags to make it easier to find notes matching certain criteria.  There is also some simple searching to even more quickly find something that has been entered.  Python is used for the program itself, wxPython is used for the GUI, and the data is stored in a SQLite database.  It is also possible to import and export the data to and from XML so that the data is not locked up in the database.

## Creating Notes ##

When the program is first opened, a new sqlite database notebook is created in the user's home folder (for example, `C:\Users\%USERNAME` in Windows 7+ or `%USERPROFILE%`). There are no notes in the notebook and the view looks like this:

![](main_view.png)

A new note can be entered in one of two ways:

* click on the New Note button in the tool bar (the first icon, looks like a sheet of paper with a green plus sign)
* click on the Notes menu and select New Note

Now this dialog will appear:

![](new_note.png)

At the very top you can see the created and modified times showing when the note was first created and when the note was last edited respectively. Notice here in a brand new note no timestamp is shown.

The first text entry box is for the subject, or title, of the note. The subject is the main topic of the note or just a quick snippet of text to describe it.

Beneath that is a text entry box for a URL if you have one that relates to the note. The Go button to the right will open the URL in your browser.

Next is the text entry box for the note's tags. Here you can add tags (separated by spaces) to the note or click on the Tags button to the right to use the tag editing dialog.

Then at the very bottom is where you enter the note text. This is the main content of the note. When you finish adding your note, click the Save note button to save the note or click on Cancel to dismiss the note without keeping it.

## Editing Notes ##

From the main notes view, a selected note can be edited in several ways:

* Select the note and click on the edit note button on the tool bar (looks like a piece of paper with a pencil)
* Select the note and click on the Notes menu and select Edit note
* Select the note and right click and choose "edit" from the context menu
* Double-click on the selected note

Now the note edit dialog will appear and look like this:

![](edit_note.png)

Here we can see several of the fields have been entered.

## Working with tags ##

Tags are words that have an associated meaning with the current note. In the example picture above we have added the tags "demonstration" and "example" to the note because we are demonstrating how to add tags and this is an example. There are no real restrictions to tags other than they must be separated by spaces. The primary purpose of tags is it allows another way of quickly finding notes as the main notes listing can be filtered by tags.

The edit tags dialog can also be used which simplifies the task of adding tags as it shows a listing of all of the tags that are currently in the notebook and allows them to be quickly applied to the current note. Select a tag from the All Tags listing and either click the Use button or double-click on it to associate it with the current note and put it in the Current tags list box. Then to remove a tag association, select a tag and click on the Remove button or double-click on it.

![](editing_tags.png)

## Deleting Notes ##

To delete a note:

* Select the note and click on the delete tool bar button (looks like a piece of paper with a red minus sign)
* Select the note and right click and choose "delete" from the context menu
* Select the note and click on the Notes menu and select Delete note

## Working with unicode ##

Note Snatcher supports Unicode text so if you paste Unicode text into your note it will be saved just like regular text.

![](text_format.png)

## Filtering Notes ##

The main window's listing of all of the notes can easily be filtered by using tags that have been assigned to the notes.

First, go to the filter by tags dialog. This is done by clicking on the View menu and then `Filter by tags...` or by clicking on the Filter by Tags icon on the toolbar (the grid with a gear, fourth from the left).

Now you will see a dialog that looks something like this:

![](filtering_by_tags.png)

### The edit tags dialog. ###

On the left there is a listing of all of the tags that are in the notebook. On the right there is a list of the tags that are currently being applied as filters. In the middle, buttons can be used to change how tags are being used. To use the selected tag from the All Tags list box, click the Use button. To remove a tag that is currently being applied, select it in the Current Tags list box and click on Remove. This dialog can also be used to remove tags from the notebook. First select a tag in the All Tags list box and then click Remove. Every note that was previously associated with that tag will no longer have that association and the tag will be gone forever.

Once some tags have been added to the Current Tags list box, only notes that match those tags will be shown on the main notes listing.

Here notes have been filtered so that only one note is being shown. On the status bar the program says that it is showing 1 out of 3 tags.

![](filtered_view.png)

To return the view to normal and show all notes no matter the tag, click the Refresh button on the toolbar (fifth from left, the two green circular swirly arrows) or click on the View menu and select Show All Notes.

## Searching Notes ##

To quickly find a note, the notebook can be searched. To do this, just enter the search term or terms in the search box in the tool bar and click on the Find button in the tool bar (the binoculars).

The search results appear in the main listing. Here we have searched for "unicode" and one note was found which had the search term in its subject. The status bar also alerts us that search results are being shown.

![](search_results.png)

To return the notes listing to its normal view that shows all notes, click the Refresh button on the toolbar (fifth from left, the two green circular swirly arrows) or click on the View menu and select Show All Notes.

## Importing and Exporting ##

Importing and exporting are straight forward operations. From the File menu, select either Import... or Export... and select a file name just like you were saving a file.

When exporting notes, you can choose between XML, HTML, or text.

Exporting XML is a useful way to back up your notes in a text-based format you can easily read, edit, or later import back into the program.

HTML and text are for when you want to backup your notes in an easy-to-read format. Note that HTML and text cannot be imported back in.

As mentioned, the only format that can currently be imported is XML that has previously been exported. When importing, notes are added to any existing notes in the currently opened notebook and nothing is replaced. So keep that in mind.

## Options ##

Access the options through File > Options.... There are two main sections, Notebook settings and Appearance settings.

![](prefs.png)

Notebook settings let you select whether or not to automatically open the last used notebook when you first start the program, whether or not to show a confirmation when you delete a note, and whether or not you want to save deleted notes to the trash or delete them permanently. These help you deal with those situations where you might accidentally delete a note before you are done with it by showing you a confirmation when deleting or keeping them safe in the trash can for later reviewal.

Appearance settings let you change the default sort order when first openeing the program (note that you can manually change the sort while viewing your notes). You can also choose whether or not to minimize or close the window to the notification area (systray) at the bottom right of the screen in Windows.

The options are stored in the user's home folder (`%USERPROFILE%`, for example, `C:\Users\%USERNAME%` in Windows 7+).

## License

GNU General Public License v3. [See LICENSE](LICENSE)

## Credits ##

The toolbar icons are from FatCow: [Free FatCow-Farm Fresh Icons](http://www.fatcow.com/free-icons)
