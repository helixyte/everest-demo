Building *everest* applications
===============================

In this section, you will find a step-by-step guide on how to build a
``REST``ful application with :mod:`everest`.


1. The application
------------------

Suppose you want to write a program that helps a garden designer with composing
lists of beautiful perennials and shrubs that she intends to plant in her
customer's gardens. Let's call this fancy application "Plant Scribe". In its
simplest possible form, this application will have to handle customers,
projects (per customer), sites (per project), and plant species (per site).


2. Designing the entity model
-----------------------------

:mod:`everest` applications keep their value state in :term:`entity` objects.

.. sidebar:: Entities and Resources

   The entity model implements the :term:`domain logic` of the application by
   enforcing all value state constraints at all times.

   Entities are manipulated through :term:`resource` objects. A resource
   object provides access either to a single entity object
   (:term:`member resource`) or to a collection of entities of the same kind
   (:term:`collection resource`). Resources can call other resources to modify
   other parts of the entity model, thus implementing the 
   :term:`business logic` of the application.

   Each collection resource uses an :term:`aggregate` to provide access to its
   underlying entities. Aggregates support slicing, filtering, and ordering
   operations.

The first step on our way to the Plant Scribe application is therefore to decide
which data we want to store in our entity model. We start with the customer:

.. literalinclude:: ../plantscribe/entities/customer.py
   :language: python
   :linenos: 

In our example, the :class:`Customer` class inherits from the :class:`Entity`
class provided by :mod:`everest`. This is convenient, but not necessary; any
class can participate in the entity model as long as it implements the
:class:`everest.entities.interfaces.IEntity` interface. Note, however, that
this interface requires the presence of a ``slug`` attribute, which in the case
of the customer entity is given in the form ``<last name>-<first name>``.


.. sidebar:: Slugs

   A :term:`slug` is a character string that uniquely identifies an entity
   within its aggregate. :mod:`everest` uses the slug to generate an URL
   for the member resource wrapping an entity, so, ideally, it should be a 
   short, mnemonic expression.

For each customer, we need to be able to handle an arbitrary number of
projects:

.. literalinclude:: ../plantscribe/entities/project.py
   :linenos: 

Note that the ``name`` attribute, which serves as the project entity slug, does
not need to be unique among *all* projects, but just among all projects for a
given customer.

Another noteworthy observation is that although the project references the
customer, we do not (yet) have a way to access the projects associated with a
given customer as an attribute of its customer entity. Avoiding such circular
references allows us to keep our entity model simple, but we may be missing the
convenience they offer. We will return to this issue a little later.

Each project is referenced by one or more planting sites:

.. literalinclude:: ../plantscribe/entities/site.py
   :linenos: 

The plant species to choose from for each site are modeled as follows:

.. literalinclude:: ../plantscribe/entities/species.py
   :linenos: 

Finally, the information about which plant species to use at which site and in
which quantity is modeled as an "incidence" entity:

.. literalinclude:: ../plantscribe/entities/incidence.py
   :linenos:


3. Designing and building the resource layer
--------------------------------------------

With the entity model in place, we can  now proceed to designing the resource
layer. The first step here is to define the marker interfaces that
:mod:`everest` will use to access the various parts of the resource system.
This is very straightforward to do:

.. literalinclude:: ../plantscribe/interfaces.py
   :linenos:

Next, we move on to declaring the resource attributes using :mod:`everest`'s
resource attribute descriptors. Each resource attribute descriptor maps a
single attribute from the resource's entity and makes it available for access
from the outside.

.. sidebar:: Resource Attribute Kinds 

   There are three kinds of resource attributes in :mod:`everest`: Terminal
   attributes, member attributes, and collection attributes. A *terminal*
   resource attribute references an object of an atomic type or some other type
   that is not a resource itself. A *member* resource attribute references
   another member resource and a *collection* resource attribute references
   another collection resource. Resource attributes are declared using the
   :func:`terminal_attribute`, :func:`member_attribute`, and
   :func:`collection_attribute` descriptor generating functions from the
   :mod:`resources.descriptors` module. 

In our example application, the resources mostly declare the public attributes
of the underlying entities as attributes:

.. literalinclude:: ../plantscribe/resources/customer.py
   :linenos:

.. literalinclude:: ../plantscribe/resources/project.py
   :linenos:

.. literalinclude:: ../plantscribe/resources/site.py
   :linenos:

.. literalinclude:: ../plantscribe/resources/species.py
   :linenos:

.. literalinclude:: ../plantscribe/resources/incidence.py
   :linenos:

In the simple case where the resource attribute descriptor declares a public
attribute of the underlying entity, it expects the type (for terminal
attributes) or the marker interface (for member and collection attributes) of
the target object and the name of the corresponding entity attribute as
arguments.

The :func:`member_attribute` and :func:`collection_attribute` descriptors also
support an optional argument ``is_nested`` which determines if the URL for the
target resource is going to be formed relative to the root (i.e., as an
absolute path) or relative to the parent resource declaring the attribute.

.. sidebar:: URL resolution 

   :mod:`everest` favors and facilitates object traversal for URL resolution.
   In particular, all resource attributes that target a collection resource 
   can be used directly for URL traversal. For :func:`member_attribute` 
   descriptors, the ``is_nested`` parameter needs to be enabled for the
   traversal to work.

We also have the possibility to declare resource attributes that do not
reference the target resource directly through an entity attribute, but
indirectly through a "backreferencing" attribute. In the example code, this is
demonstrated in the ``projects`` attribute of the :class:`CustomerMember`
resource which allows us to access a customer's projects at the resource level
even though the underlying entity does not reference its projects directly.

Note that every member resource class needs to have a ``relation`` attribute
that uniquely identifies the class. :mod:`everest` maintains a mapping of
resource interfaces to relation strings internally which is used e.g. for class
hinting when parsing JSON representations (see
:ref:`using-different-mime-content-types`).


4. Configuring the application
------------------------------

With the resource layer in place, we can now move on to configuring our
application. :mod:`everest` applications are based on the :mod:`pyramid`
framework and everything you learned about configuring :mod:`pyramid`
applications can be applied here. Rather than duplicating the excellent
documentation available on the Pyramid web site, we will focus on a minimal
example on how to configure the extra resource functionality that
:mod:`everest` supplies.

Settings
^^^^^^^^

Settings are used for configuration values that may have
different values for each deployment and are kept in an ``.ini`` file. The
default settings file for the ``plantscribe`` application looks like this:

.. literalinclude:: ../plantscribe.ini

The ``[app:plantscribe]`` section specifies a file system directory for the
resource repository (contains the initial data to load) and a ``Paster``
application factory (responsible for creating and setting up the application
registry and for instantiating a ``WSGI`` application), enables the ``Pyramid``
transaction manager (ensures a ``commit`` or ``rollback`` is issued at the end
of each request) with the default commit veto supplied by :mod:`everest` and
configures the ``public`` folder inside the deployment folder for static
content.

The remaining sections configure the server (``[server:main]``), the ``WSGI``
application stack (``[pipeline:main]``) and the logging subsystem
(``[loggers]`` and the following sections) in a manner typical for ``Pyramid``
applications.

Configuration
^^^^^^^^^^^^^

.. sidebar:: The Zope Component Architecture (``ZCA``)

   Originally developed for the Zope web application server, the ``ZCA`` is a 
   framework for component based design of software applications. Components
   are reusable objects with introspectable interfaces which can be configured
   at runtime; this, for instance, makes it easy to substitute arbitrary
   domain model classes with dummy versions for unit testing. An excellent 
   introduction to the ZCA can be found 
   `here http://www.muthukadan.net/docs/zca.html`. 

:mod:`everest`, like ``Pyramid``, makes extensive use of the Zope Component
Architecture.

The ``.zcml`` configuration file - which is loaded through the application
factory - contains all high-level component declarations for our ``plantscribe``
application:

.. literalinclude:: ../plantscribe/configure.zcml
   :language: xml
   :linenos:

Note the ``include`` directive at the top of the file; this not only pulls in
the :mod:`everest`-specific ``ZCML`` directives, but also the ``Pyramid``
directives as well.

The ``filesystem_repository`` directive sets up a default resource repository
in the file system. A resource repository serves as an accessor for fetching
resources from and storing resources to some persistency backend. We will
return to the topic of setting up and configuring resource repositories later.

The ``representer`` directive is used to define generic configuration values for
representers. Representers are used to convert resources to a representation of
a particular ``MIME`` content type such as ``application/csv``. The generic
representer configuration values provide defaults for subsequent representer
configurations on a per-resource basis which we also discuss later in detail.

The most important of the :mod:`everest`-specific declarations are made using
the ``resource`` directive. In the example application, the resources are
declared in a separate ``ZCML`` file (only the declarations for the
``ICustomer`` resource are shown for brevity):

.. literalinclude:: ../plantscribe/resources.zcml
   :lines: 1-45,170-
   :language: xml
   :linenos:

.. sidebar:: The resource subsystem

   This graphics shows the relationship of the four main components of the
   resource subsystem for a hypothetical resource ``Foo``. At the center is 
   the marker interface ``IFoo`` with which all other components can be 
   retrieved (and configured) at runtime.
   
   |resource_classes|
   
.. |resource_classes| image:: resource_classes.png

Each ``resource`` directive sets up the various components of the
resource subsystem, using our marker interfaces as the glue. At the minimum,
you need to specify

- A marker interface for your resource;

- An entity class for the resource;

- A member class class for the resource; and

- A name for the root collection.

The aggregate and collection objects needed by the resource subsystem
are created automatically; you may, however, supply a custom collection class
that inherits from :class:`everest.resources.base.Collection`. If you do not
plan on exposing the collection for this resource to the outside, you can set
the ``expose`` flag to ``false``, in which case you do not need to provide a
root collection name. Non-exposed resources will still be available as a root
collection internally, but access through the service as well as the generation
of absolute URLs for them will not work.

Each ``resource`` directive may contain one or several ``representer``
directives which specify how this resource should be converted to a particular
``MIME`` content type representation and vice versa. You always need to specify
the ``content_type`` (``MIME`` type); in addition, you may specify the resource
``kind`` to configure as either "``member``" or "``collection`` to indicate
that the following declarations should only apply to the member or collection
representer for the enclosing resource, respectively. The representer
configuration is specified using one or several ``option`` tags which have a
``name``, a ``value`` and an optional ``type`` attribute. Individual resource
attributes can be configured using ``attribute`` tags. We will explain this
feature in more detail later.

With the resources fully configured, we can now move to the view declarations.
:mod:`everest` provides three view directives, ``resource_view``,
``member_view``, and ``collection_view``. All three are convenience wrappers
around the standard ``Pyramid`` view declaration and accept the same options as
the latter except for the following differences:

* The ``for_`` option accepts not one, but any number of context specifiers.
  You can use also use resource interfaces here;
* The ``request_method`` option has special meaning in the resource view
  directives in that, together with the value of the ``for_`` option, it
  allows :mod:`everest` to determine which view class to use. The following
  table shows the rules for this view autodetection feature:

  ========================= ===================== ========================
  **Context Resource Kind** **Request Method**    **Default View Class**
  ========================= ===================== ========================
  Collection                GET                   GetCollectionView
  Collection                POST                  PostCollectionView
  Member                    GET                   GetMemberView
  Member                    PUT or FAKE_PUT       PutMemberView
  Member                    DELETE or FAKE_DELETE DeleteMemberView
  ========================= ===================== ========================

  The ``FAKE_PUT`` and ``FAKE_DELETE`` values for the ``request_method``
  option instruct :mod:`everest` to register a view that will respond to
  ``POST`` requests that have the ``X-HTTP-Method-Override:PUT`` or the
  ``X-HTTP-Method-Override:DELETE`` header set with a ``PUT`` or ``DELETE``
  operation, respectively. This is useful for clients that offer no support
  for ``PUT`` or ``POST`` (e.g., Flex).

  You can suppress automatic view detection by explicitly passing in a value
  for the ``view`` option. Note that you can also specify several request
  method arguments in one view declaration to register the associated view
  for each request method in a single directive.

  In addition to the default view, named views are registered for all builtin
  representers so that the client can address representations of different
  ``MIME`` content types directly using a ``URL`` suffix:

  ============= ==================== ===============
  **View Name** **MIME Type**         **URL Suffix**
  ============= ==================== ===============
  csv           application/csv      /@@csv
  json          application/json     /@@json
  xml           application/xml      /@@xml
  atom          application/xml+atom /@@atom
  ============= ==================== ===============

* The ``default_content_type`` option determines the ``MIME`` type of the
  representation returned in the response when the client does not indicate a
  preference.

There is only one difference between the three custom :mod:`everest` view
directives: When a resource interface is used as value for the ``for_`` option
in the ``resource_view`` declaration, the specified view is registered for
both the associated member and collection resource classes whereas in the
``collection_view`` and the ``member_view`` directives the view is only
registered for the collection resource class and member resource class,
respectively.


5. Running the application
--------------------------

To see our little application in action, we first need to check out the
latest sources for the :mod:`everest-demo` project from github:

.. code-block:: text

   $ git clone https://github.com/cenix/everest-demo.git 

Then, install the ``plantscribe`` demo application by issuing

.. code-block:: text

   $ pip install -e .
   
inside the root folder of the ``everest-demo`` project [#f1]_ .

Next, set up a deployment folder of your liking, e.g.

.. code-block:: text

   $ cd
   $ mkdir webapps
   $ mkdir webapps/plantscribe
   
and populate it with the following files from the ``everest-demo`` project
folder [#f2]_ :

.. code-block:: text

   $ cd webapps/plantscribe
   $ cp -R ~/git/everest-demo/schemata .
   $ cp -R ~/git/everest-demo/plantscribe.ini .
   
If you want to start out with a few sample data rather than a completely empty
repository, you can also copy the data folder from the unit testing tree into
the deployment folder:

.. code-block:: text

   $ cp -R ~/git/everest-demo/plantscribe/tests/data . 

Now, we can use the ``pshell`` interactive shell that comes with ``Pyramid`` to
explore the ``plantscribe`` application interactively from the command line
like this:

.. code-block:: text

   $ cd webapps/plantscribe
   $ pshell plantscribe.ini 
   Python 2.7.2 (v2.7.2:8527427914a2, Jun 11 2011, 15:22:34)
   [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
   Type "help" for more information.
   
   Environment:
     app          The WSGI application.
     registry     Active Pyramid registry.
     request      Active request object.
     root         Root of the default resource tree.
     root_factory Default root factory used to create `root`.

   >>> 

The ``root`` object that is available in the ``pshell`` environment is the
service object that provides access to all public root collections by name:

.. code-block:: text

   >>> c = root['customers']
   >>> c 
   <CustomerMemberCollection name:customers parent:Service(started)>

We can now start adding members to the collection and retrieve them back from
the collection:

.. code-block:: text

   >>> from plantscribe.entities.customer import Customer
   >>> ent = Customer('Peter', 'Fox')
   >>> m = c.create_member(ent)
   >>> m.__name__
   'fox-peter'
   >>> c.get('fox-peter').__name__
   'fox-peter'

To run the server, exit the pshell (``CTRL-D``) and use the ``paster`` command
from the command line:

.. code-block:: text

   $ paster serve plantscribe.ini
   
With a tool like the excellent
`REST client <http://code.google.com/p/rest-client/>`_ you can now explore the
server response for various ``REST`` requests, e.g. a simple ``GET`` request to
the ``URL`` ``http://localhost:5432/customers``.


6. Adding persistency
---------------------

With the application running, we now turn our attention to persistency.
:mod:`everest` uses a :term:`repository` to load and save resources from and to
a storage backend.

By default, :mod:`everest` uses a non-persisting memory repository as
resource repository. With the following ``ZCML`` declaration, a
filesystem-based repository is used as the default for our application:

.. code-block:: xml

   <filesystem_repository
      directory="data"
      content_type="everest.mime.CsvMime"
      make_default="true" />

This tells :mod:`everest` to use the ``data`` directory (relative to the
deployment directory) to persist representations of the root collections of
all resources as ``.csv`` (Comma Separated Value) files. When the application
is initialized, the root collections are loaded from these representation files
and during each ``commit`` operation at the end of a transaction, all modified
root collections are written back to their corresponding representation files.

The filesystem-based repository does not perform well with complex or high
volume data structures or in cases where several processes need to access the
same persistency backend. In these situations, we need to switch to a database
repository. :mod:`everest` uses ``SQLAlchemy`` as ``ORM`` for relational
database backends. What follows is a highly simplified account of what is
needed to instruct ``SQLAlchemy`` to persist the entities of an :mod:`everest`
application; for an explanation of the terms and concepts used in this section,
please refer to the excellent documentation on the
`SQLAlchemy web site <http://sqlalchemy.org/>`_ .

In a first step, we need to initialize the relational database backend and the
``ORM`` as shown in the following ``ZCML`` declaration (which also makes the
``rdb`` repository the default repository):

.. code-block:: text

    <rdb_repository
        metadata_factory="plantscribe.create_metadata"
        make_default="true"/>

The metadata factory setting references a callable that takes an ``SQLAlchemy``
engine as a parameter and returns a fully initialized metadata instance. For
our simple application, this function looks like this:

.. literalinclude:: ../plantscribe/rdb.py
   :linenos:
   :lines: 53-

The function first creates a database schema and then maps our entity classes to
this schema. Note that a special mapper is used which provides a convenient way
to map the special `id` and `slug` attributes required by :mod:`everest` to the
``ORM`` layer.

To use an engine other than the default in-memory ``SQLite`` database engine,
you need to supply a ``db_string`` setting in the paster application ``.ini``
file. For example, to use ``Postgres`` with the ``psycopg2`` adapter, you would
use something like this:

.. code-block:: text

   [DEFAULT]
   db_server = mydbserver
   db_port = 5432
   db_user = mydbuser
   db_password = mypassword
   db_name = mydbname
   
   [app:myapp]
   db_string = postgresql+psycopg2://%(db_user)s:%(db_password)s@%(db_server)s:%(db_port)s/%(db_name)s
   
Note that while you can not have two default repositories, you could very well
have one or more ``filesystem_repository`` declarations for individual
resources, possibly even pointing to different directories in your file system.

Different resorces may use different repositories, but any given resource can
only be assigned to one repository.


.. rubric:: Footnotes

.. [#f1] If you use ``easy_install`` as your package manager, the equivalent 
         invocation would be "``easy_install develop .``".
.. [#f2] This step will eventually be automated with a paste script.