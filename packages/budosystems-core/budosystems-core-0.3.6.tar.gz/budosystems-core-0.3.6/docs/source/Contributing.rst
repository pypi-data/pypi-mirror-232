Contribute to Budo Systems
==========================

File Issues
-----------

You can report bugs, request features, point out documentation errors, etc.

To do so, go to the `project's Issues page <issues_>`_, and click on :guilabel:`New issue`.

.. </issues_> This is so dumb... PyCharm should know the difference between rST links and *ML tags... Ugh!!!

Share Your Expertise
--------------------

FOSS Project Management
~~~~~~~~~~~~~~~~~~~~~~~

We need people who know how to effectively organize and manage a software project, and more specifically, an open
source project.

Martial Arts Management
~~~~~~~~~~~~~~~~~~~~~~~

We need the expertise of martial arts school owners, managers, instructors, and other staff, to ensure that we have
optimal coverage of needs for this type of business.

Software Engineering
~~~~~~~~~~~~~~~~~~~~

We need programmers who understand Principles of Design Patterns and how to make most effective use of them for this
project.

Technical Writing
~~~~~~~~~~~~~~~~~

Many FOSS projects suffer from having poor documentation.  We hope to avoid that plight.  If you have expertise in this
area, we would greatly appreciate your help.

Code with Us
------------

Regardless of whether or not you fit in the expertise areas listed above, you are welcome to contribute to the code
of this project.  Here are some considerations for programming with us.

VCS: Git on GitLab
~~~~~~~~~~~~~~~~~~

Our GitLab repository: https://gitlab.com/budosystems/budosystems-core

Programming Language: Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core model and supporting code is written in pure Python.  All the code is typed.  You can see more details about
the :doc:`design` and the :doc:`api` for a better understanding.

* We use ``pylint`` for lint checking the code.
* We use ``mypy`` for static type checking the code.
* We use ``pytest`` to run our test suites.

Documentation: reStructuredText
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The source of the documentation is written in reStructuredText and processed by Sphinx.  As such, we use Sphinx
extensions and plug-ins.

Additionally, the doc strings in the python code is written in reStructuredText syntax.

Code of Conduct
~~~~~~~~~~~~~~~

The gist of our code of conduct is "Be respectful".  Read the full :doc:`CodeOfConduct` page for more details.

Support Our Other Projects
--------------------------

This particular project is the core of the software.  However, it's not designed to be an autonomous program.  Instead,
it requires other components to drive it.  In particular, at minimum, there needs to be a storage component and a
view/interaction component.  Our other projects will provide reference implementations for these components.

Here are some examples of related projects we'd like to develop.

.. container:: two-col

  .. container:: left-col

    Storage:

    * MySQL relational storage
    * MongoDB document storage
    * ArangoDB graph storage

  .. container:: right-col

    View / Interaction:

    * :abbr:`CLI (Command Line Interface)` client
    * :abbr:`REST (Representational State Transfer)` public interface
    * :abbr:`HTML (HyperText Markup Language)` interface


Expand in Your Own Open Source Projects
---------------------------------------

See some gaps that aren't being filled by any of our projects?
You're more than welcome to create one of your own to fill that gap, and share it with the Budo Systems community.

Tell the World About Budo Systems
---------------------------------

Share this project with your peers.

Ultimately, the goal is for martial arts school owners to use Budo Systems to run their businesses.
The vast majority of these people don't have an alter-ego who's a developer.
Maybe the various "official" components will be sufficient for them to do so.
Or maybe they'll need to have some custom code written for them.

.. _issues: https://gitlab.com/budosystems/budosystems-core/-/issues
