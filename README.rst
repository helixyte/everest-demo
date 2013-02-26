=============================================
everest-demo - Demo application for *everest*
=============================================

Sample application and tutorial demonstrating how to build RESTful applications
with ``everest``.


For the impatient: Getting the Demo application up and running
==============================================================

If you just want to play with an ``everest`` application without having to go
through boring background information, do the following:

1. Follow the
`installation instructions <https://github.com/cenix/everest#installation>`_
for ``everest``;

2. Check out the sources of the ``everest`` demo project:

``$ git clone https://github.com/cenix/everest-demo.git``

3. Install the demo app:

::

  $ cd everest-demo

  $ pip install -e .

  $ cd webapps/plantscribe

  $ cp -R ~/git/everest-demo/schemata .

  $ cp -R ~/git/everest-demo/plantscribe.ini .

  $ cp -R ~/git/everest-demo/plantscribe/tests/data .

4. Start the application:

``$ paster serve plantscribe.ini``



For the serious: Studying the tutorial
======================================

The tutorial explains the concepts behind ``everest`` and explains how to build,
use and customize RESTful applications with ``everest`` using the demo
application as an example. You can find the tutorial
`here <http://cenix.github.com/everest-demo>`_.