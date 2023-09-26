platform-plugin-notices
=============================

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge| |license-badge|

**This repo is not currently accepting open source contributions**

Overview
--------

This plugin for edx-platform manages notices that a user must acknowledge. It only stores the content of the notices and whether a user has acknowledged them. Presentation and other client side decisions will be left to the frontends that utilize these APIs.

This Django app contains notices that a user must acknowledge before continuing to use the site. This app will have two API endpoints to facilitate that:
1. An endpoint to return links to all notices that the user hasn't acknowledged.
2. An endpoint to acknowledge that a user has seen the notice. This endpoint's URL will be passed to the client via the first endpoint.

Documentation
-------------

(TODO: `Set up documentation <https://openedx.atlassian.net/wiki/spaces/DOC/pages/21627535/Publish+Documentation+on+Read+the+Docs>`_)

Developing in Devstack
~~~~~~~~~~~~~~~~~~~~~~
Make sure the LMS container is running in Devstack, then

.. code-block::

  git clone git@github.com:edx/platform-plugin-notices.git <devstack_folder>/src
  cd <devstack_folder>/devstack
  make dev.shell.lms
  pip install -e /edx/src/platform-plugin-notices
  cd /edx/app/edxapp/edx-platform
  ./manage.py lms migrate

Once that is done, LMS will pickup the plugin and saves to existing files should cause a devserver restart with your changes. Occasionally when adding a new file, you may need to restart the LMS container in order for it to pickup the changes.

Enabling the Notices Plugin in the LMS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Notices plugin functionality is enabled via use of a waffle flag. After installation of the plugin you need to do the following in devstack:

#. Log into the LMS Django Admin (http://localhost:18000/admin/)
#. Add a new waffle flag (http://localhost:18000/admin/waffle/flag/add/)
#. Name the waffle flag ``notices.enable_notices``
#. Set `Everyone` to `Yes`
#. Save the waffle flag.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

How To Contribute
-----------------

This repo is not currently accepting open source contributions

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Support
-------

If you're having trouble, we have discussion forums at https://discuss.openedx.org where you can connect with others in the community.

Our real-time conversations are on Slack. You can request a `Slack invitation`_, then join our `community Slack workspace`_.

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx-slack-invite.herokuapp.com/
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-notices.svg
    :target: https://pypi.python.org/pypi/edx-notices/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/edx/platform-plugin-notices/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/edx/platform-plugin-notices/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/edx/platform-plugin-notices/coverage.svg?branch=main
    :target: https://codecov.io/github/edx/platform-plugin-notices?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/platform-plugin-notices/badge/?version=latest
    :target: https://platform-plugin-notices.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-notices.svg
    :target: https://pypi.python.org/pypi/platform-plugin-notices/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/platform-plugin-notices.svg
    :target: https://github.com/edx/platform-plugin-notices/blob/main/LICENSE.txt
    :alt: License
