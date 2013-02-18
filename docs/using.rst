Using *everest* applications
============================


1. Querying with GET
--------------------

The Collection Query Language (CQL)
___________________________________

One of the main features of the collection resources in :mod:`everest` are
their advanced filtering, ordering and batching capabilities. Query strings
have to conform to a custom query language, the Collection Query Language
(CQL).

A CQL query consists of a filtering part, an ordering part, and a batching
part. All parts are optional; if they are omitted, the collection is returned
unfiltered using the default sort order and the default batch size defined
by the collection (if specified).

The filtering part of a CQL query (prefixed with the string ``q=``) consists of
one or more criteria of the form

         ``resource attribute name ":" operator ":" value``

Example: ``last-name:equal-to:"Doe"``

It is possible to supply multiple criterion values in a comma separated
list, which will be interpreted as a Boolean "OR" operation on all given
values.

Supported types for a CQL criterion value are:

String
   Arbitrary string enclosed in double quotes.
Number
   Integer or floating point, scientific notation allowed.
Boolean
   Case insensitive string **true** or **false**.
Date/Time
   ISO 8601 encoded string enclosed in double quotes.
Resource
   URL referencing a resource.

The ordering part of a CQL query (prefixed with the string ``sort=``)
consists of one or more order criteria of the form

         ``resource attribute name ":" operator``

where the operator is one of ``asc`` (ascending sort order) or ``desc``
(descending sort order).

Example: ``last-name:asc``

In filtering and ordering query expressions, you can specify a dotted
identifier as the resource attribute name to query nested resources. Also,
multiple CQL filter and order criteria can be combined using the two logical
operators "`AND`" and "`OR`". "`AND`" expressions have precedence over
"`OR`" expressions. The precedence rules can be overridden using open and
close parentheses ("`(`" and "`)`"). Using the tilde ("~") character as a
shorthand for the "`AND`" operator is also supported; note, however, that you
can not combine a criteria expression that uses the tilde character with one
that uses the standard `AND` and `OR` operators.

The batching part of a CQL query can be used to specify a batch size (with
an expression of the form ``"size" "=" batch size`` where ``batch size`` is
an integer) and a batch number (with an expression of the form
``"offset" "=" batch offset`` where ``batch offset`` is an integer).

The following table shows the available operators and data types in CQL:

============================  ======== ====== ======= ========== ========
        Operator                              Data Type
----------------------------  -------------------------------------------
        Name                  String   Number Boolean Date/Time  Resource
============================  ======== ====== ======= ========== ========
    ``starts-with``              x
  ``not-starts-with``            x
    ``ends-with``                x
  ``not-ends-with``              x
    ``contains``                 x                                   x
  ``not-contains``               x                                   x
   ``contained``                 x        x      x         x         x
 ``not-contained``               x        x      x         x         x
    ``equal-to``                 x        x      x         x         x
  ``not-equal-to``               x        x      x         x         x
    ``less-than``                         x
``less-than-or-equal-to``                 x
   ``greater-than``                       x
``greater-than-or-equal-to``              x
     ``in-range``                         x
============================  ======== ====== ======= ========== ========

All attributes that are used to compose a query expression need to be mapped
column properties in the ORM. Aliases are supported, CompositeProperties are
not. All queried entities must have an "id" attribute.

It is by design that the power of CQL to express complex queries is far behind
that of SQL. CQL aims to provide a simple, uniform querying language for
all collection resources of an applciation regardless of the persistency
backend used.


GET request processing
______________________

A GET request to a collection resource with a query string such as

`<http://localhost:6543/customers?q=first-name:startswith:"J"?order=last-name:asc?size=100>`_

is processed by :mod:`everest` as follows:

 1. The context and its associated view are identified just as in any vanilla
    :mod:`Pyramid` application. In the example, this would be the ``customers``
    collection resource at the root of the object tree (the "root collection")
    and the :class:`everest.views.getcollection.GetCollectionView`;
 2. The view parses the query string submitted by the client (in the example,
    the ``q=first-name:startswith:"J"`` part of the URL) into a resource
    filter specification and applies it to the context collection resource.
    This triggers a translation of the resource filter specification into
    an entity filter specification which is then applied to the underlying
    aggregate. This separation of resource and entity level attributes does
    only make it possible to expose entity attributes under a different name
    at the level of the resource, but also to expose attributes from nested
    entities (using "dotted" identifiers);
 3. The view processes the order string (``order=last-name:asc``) in the same
    fashion as the query string;
 4. The view parses the batch size string (``size=100``) and applies this
    setting to the context collection resource;
 5. The view iterates over the context collection resource and wraps the
    filtered, ordered, and batched member resources into a new result
    collection resource;
 6. Using a representer, the view creates a string representation of the
    appropriate content type (either requested by the client
    or statically defined for the resource) from the result collection;
 7. The view fills the response body with the representation, sets up the
    response headers and returns the response for further processing through
    the WSGI stack.

2. Customizing representations
------------------------------

The default behavior of the :mod:`everest` representers is to

 * Represent all terminal attribute values as the value obtained by result of ;
 * Represent nested member resources as links (URLs); and
 * Ignore nested collection resources.

Nested collections are ignored by default because retrieving a collection can
be very expensive and even generating a URL for a collection typically requires
iterating over all its members.

To change these defaults for a given resource attribute, we set the appropriate
``representer``, ``attribute`` and ``option`` tags inside a ``resource``
declaration. For example, to include the nested ``projects`` collection in
``XML`` representations of ``customer`` members we would include the
following declaration in the ``ZCML`` configuration file:

.. code-block:: xml

   <representer
      kind="member"
      content_type="everest.mime.XmlMime"
   >
      <attribute name="projects">
          <option
              name="ignore"
              value="false" />
          <option
              name="write_as_link"
              value="false" />
      </attribute>
   </representer>

The ``ignore`` option is a shorthand for setting both the ``ignore_on_read``
and the ``ignore_on_write`` option which set the ignore behavior selectively
when a representation is parsed (``ignore_on_read``) or generated
(``ignore_on_write``). The ``write_as_link`` option ensures that the nested
resource is represented as a (URL) link rather than as an explicit
recursive representation of all its attributes.
