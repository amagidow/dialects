---------------------------
Database of Arabic Dialects
---------------------------
Programmer's Readme
+++++++++++++++++++

The Database of Arabic dialects (ضاد) is a Django-driven website built on an extremely flexible database structure that
allows for a wide variety of linguistic data. The underlying database structure, as well as the Django views, could be used for
almost any language in which there is a need to compare a large number of different lects. Modification would need to be made to 
some of the webpages and source, but could be completed fairly quickly. All of the code is made available via a GPL license.

State of the project
####################
As of 6/26/2015

This is a working, usable version of the website and database that is also in need of significant bug elimination work and addition of
new features. Users who are not logged in can visualize public data in a variety of ways. Users who are logged in can enter data, but
for the current phase of the project access to data entry will be heavily restricted while bugs and workflow slowdowns are determined
and repaired. 

Contributing to the project
###########################
There are two primary ways contributors can assist the project at the moment. The first is to submit data, whether via the website or
by submitting a CSV type file, and to test data entry and data visualization components. The second is to contribute code, whether
python/django, HTML/CSS or Javascript.

Data contributions
^^^^^^^^^^^^^^^^^^
Data contributors are needed for two main purposes: Ensuring that the database structure is robust enough to handle a wide variety of
of data, and to help provide specifications for useful website views. The flexibility in the database and website is meant to be
user driven, and so data contributors should work with code contributors to ensure that they can input and access their data
in a meaningful way.

All data has permissions attached to it - currently contributors can choose to have their data as public, public with no export allowed,
or entirely private. The no export option does not, however, protect against someone simply cut and pasting form the website.

One thing we ask of contributors if they are submitting CSV type data is to align their dialect and bibliographical
information with what is currently in the database, though we can certainly add more. However, that step can be time consuming so we
would prefer if it fell on data contributors rather than developers.

Code contributions
^^^^^^^^^^^^^^^^^^
Until now, this project has been developed almost entirely by Alexander Magidow of the University of Rhode Island. His skills are
primarily in Python and Django, not as much in HTML/Javascript/Jquery, so contributions in those areas are particularly appreciated.
The todo file in this directory will list tasks that need to be done and for which contributions would be appreciated. Code commenting
and documentation is ongoing as of 6/26/2015, so please excuse the mess. 

Currently contributions are only accepted by official collaborators.
Please contact lead developer Alex Magidow (amagidow AT gmail DOT com) to be added as a collaborator. 
