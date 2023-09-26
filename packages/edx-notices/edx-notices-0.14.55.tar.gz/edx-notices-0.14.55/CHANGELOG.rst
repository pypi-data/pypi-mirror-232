Change Log
----------

..
   All enhancements and patches to notices will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[0.14.55] - 2023-09-25
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Fixed PyPI Publish workflow

[0.14.53] - 2023-09-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added Django 4.2 Support

[0.14.20] - 2022-07-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Updating Python Requirements

[0.14.15] - 2022-07-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Updating Python Requirements

[0.14.11] - 2022-06-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Updating Python Requirements

[0.14.4] - 2022-02-14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Changed Do not redirect notices/render/{id}/ to login page in case of 403 on mobile request

[0.14.3] - 2022-02-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Update pip-tools

[0.14.2] - 2022-01-28
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Update Python dependencies

[0.14.1] - 2022-01-05
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Update Python dependencies

[0.14.0] - 2021-11-24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add logging

[0.13.0] - 2021-11-24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added history table to AcknowledgedNotice

[0.12.0] - 2021-11-2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added support for django 3.2 and dropped support for previous versions

[0.11.8] - 2021-11-10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Update Python dependencies

[0.11.7] - 2021-11-10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add userLanguage flag so JavaScript-rendered text can be displayed in the correct language

[0.11.6] - 2021-11-10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add mobile flag so mobile can be disabled in production

[0.11.5] - 2021-11-09
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add lang tag to HTML element

[0.11.4] - 2021-11-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Change name of segment event from "acquisition" to "notice"

[0.11.3] - 2021-11-05
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Allow user to leave page even if API call fails (important for mobile)

[0.11.2] - 2021-11-04
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Updated Django admin form list display and searchable fields.

[0.11.1] - 2021-10-29
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* fix analytics key in template

[0.11.0] - 2021-11-1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add in a setting to limit the number of days you can snooze a notice.

[0.10.3] - 2021-10-29
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Fix dismiss button redirecting

[0.10.2] - 2021-10-29
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* fix analytics key

[0.10.1] - 2021-10-29
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Limit notices to users who were created before it was released

[0.10.0] - 2021-10-25
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add segment library for event tracking

[0.9.0] - 2021-10-25
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add in a snooze limit feature that will only allow a notice to be snoozed a number of times

[0.8.2] - 2021-10-21
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Update requirements

[0.8.1] - 2021-10-21
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add ability to reshow notice after a snooze period via setting

[0.7.3] - 2021-10-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Make AcknowledgedNotice user editable in the admin for testing purposes

[0.7.2] - 2021-10-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Make AcknowledgedNotice user readonly in the admin for performance

[0.7.1] - 2021-10-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add Waffle Flag to enable and disable the feature for rollout

[0.6.1] - 2021-10-7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add Python API for retrieving unack'd and active notice data
* Add Plugin Context API for notice data to support redirects on the LMS Course Dashboard

[0.5.1] - 2021-10-7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Disallow dismissal after confirmation of notice

[0.4.1] - 2021-10-7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Allow inactive (non-email-verified) users to call APIs

[0.3.1] - 2021-10-1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add mobile calls so notice code can deep link

[0.2.2] - 2021-09-24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add fallback language on render view
* Add Bearer auth to APIs for mobile
* Add login requirement to render view
* Add first edx-platform dependency

[0.2.1] - 2021-09-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Utility functions for custom notice code to use to call APIs

[0.1.1] - 2021-09-16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Moved to server rendered notice model
* Add mandatory types to acknowledgement to track more states

[0.1.0] - 2021-08-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* First release on PyPI.
