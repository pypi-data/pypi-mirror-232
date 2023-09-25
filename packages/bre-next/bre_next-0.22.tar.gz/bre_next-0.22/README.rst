=====================
BUSINESS RULES ENGINE
=====================

The Business Rules Engine is a separate application before ISP-Invoice.

The application is created to enrich and/or transform data in the XML via
customer specific business rules, right before importing in ISP-Invoice

It can also be used without ISP-SmartScan to enrich XMLs from ie. IDT,
InvoiceSharing and other EDI-sources.

Getting started
===============

Setting up the development environment takes some steps, which are outlined
below.

### Installing dependencies
---------------------------

Ensure you have a virtualenv created and activated in the root-directory
- virtualenv --python=python3 env
- source env/bin/activate

Install the dev dependencies with **
- pip install -e ".[tests,pycodestyle,docs,dev,release]"

** Installing on Mac needs the quotes, where Windows/Linux might not.
Details: https://zsh.sourceforge.io/Guide/zshguide05.html#l137

Run unit-tests
==============

Ensure you have a virtualenv created and activated in the root-directory
Simply run Pytest
- pytest


Code coverage
=============

To view how many code has been covered during tests we use Coverage

Ensure you have a virtualenv created and activated in the root-directory
Run coverage
- coverage run --source bre -m py.test
Or to export to HTML
- coverage html -d coverage_html


Command line tool
=================

To start the BRE-tool via command line use the following command
- bretool URL-TO-INFO-API
Example:
- bretool http://localhost:8000/bre/api/info

Optional;y add debug-information in log-file;
- bretool http://localhost:8000/bre/api/info --loglevel=DEBUG

Optionally use a different log-file
- bretool http://localhost:8000/bre/api/info --logfile=PATH_TO_FILE
