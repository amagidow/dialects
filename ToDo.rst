------------------------------------------------------
To Do List of Changes/Improvements to Dialects Project
------------------------------------------------------
The following tasks are grouped by level of difficult/time commitment. It can be helpful to contact the lead developer, Alex Magidow, to inquire about any of these before undertaking them.

Last revised: 6/26/2015

Relatively Trivial
##################
Basic Web Tasks
^^^^^^^^^^^^^^^
- Add users guide
- Add links to github from About page
- Fix jinja page login bug (pages that use Jinja think anonymous users are logged in)

Login and Authentication
^^^^^^^^^^^^^^^^^^^^^^^^
- Develop new user profile creation page
- Develop method for changing passwords
- Improve contributor info page to include affiliation/website/etc

Views
^^^^^
- Add more closed-class paradigms, per user requirements
- Add alerts for near-duplicate data input
- Allow users to hide Annotation columns in paradigm input using Javascript
    * Possibly use datatables to implement this? 

Backend
^^^^^^^
- Allow searches to automatically search data in different transliteration styles
    * Should be relatively trivial with maketrans and trans (python 3)
    * Add Arabic characters as possible normalizedInput, along with search?
- Create mechanism for checking for near-duplicate data

Somewhat complex
################
Views
^^^^^
- Develop view that allows for entering both raw data, and glosses, but which does tagging/relationships behind the scenes. 

Backend
^^^^^^^
- Develop workaround to Hstore search bug/function (https://code.djangoproject.com/ticket/25021)
- Develop parser for gloss-type views

Extremely complex
##################

- Allow simple export of multiple paradigms directly to Word or similar formats
- Allow for users to download a local version of the website for use during field work, and then to upload fieldwork data later on
- Create a widget that allows for simple transformation of CSV type data into the format used in this database.
