------------------------------------------------------
To Do List of Changes/Improvements to Dialects Project
------------------------------------------------------
The following tasks are grouped by level of difficult/time commitment.

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

Backend
^^^^^^^

Extremely complex
##################

- Export to doc formats
- Local versions with reliable upload
