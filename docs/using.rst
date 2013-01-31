Using :mod:`everest` applications
=================================


Querying with GET
-----------------

.. sidebar:: Collection Query Language (CQL)

   :mod:`everest` supports a custom Collection Query Language (CQL) for
   querying collection resources.

   A CQL query consists of a filtering part, an ordering part, and a batching
   part. The filtering part (indicated 
   CQL query expressions are composed of one or more query criteria. There
   are two types of query crit which
   each consists of three parts separated by a colon (":") character :

   1. resource attribute name
      The name of the resource attribute to query. You can specify dotted 
      names to query nested resources.
   2. operator 
      The operator to apply.
   3. value 
      The value to query for. It is possible to supply multiple values
      in a comma separated list, which will be interpreted as a Boolean "OR"
      operation on all given values.
      
   An example for a CQL criterion would be `last-name:equal-to:"Doe"`.
      
   Multiple CQL criteria can be combined using the two logical operators
   "`AND`" and "`OR`" where "`AND`" expressions have precedence over "`OR`" 
   expressions. The precedence rules can be overridden using open and close
   parentheses ("`(`" and "`)`").
   
   :mod:`everest` also supports using the tilde ("~") character as a 
   shorthand for the "`AND`" operator. Note, however, that you can not 
   combine a criteria expression that uses the tilde character with one
   that uses the standard `AND` and `OR` operators.
      
   Supported value types for a CQL criterion are:

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

One of the main features of the collection resources in :mod:`everest` are
their advanced filtering, ordering and batching capabilities.

Query strings have to conform to a custom query language (see sidebar
"Collection Query Language" for details).


A GET request to a collection resource with a query string such as

http://localhost:6543/customers?q=first-name:startswith:"J"?order=last-name:asc?size=100

is processed by :mod:`everest` as follows:

 1. The context and its associated view are identified just as in any vanilla
    :mod:`Pyramid` application. In the example, this would be the ``customers``
    collection resource at the root of the object tree (the "root collection")
    and the :class:`everest.views.getcollection.GetCollectionView`;
 2. The view parses the query string submitted by the client (in the example,
    the ``q=first-name:equal-to:John`` part of the URL) into a resource
    filter specification and applies it to the context collection resource.
    This triggers a translation of the resource filter specification into
    an entity filter specification which is then applied to the underlying
    aggregate. This separation of resource and entity level attributes makes
    it not only possible to expose entity attributes under a different name
    at the level of the resource, but also to expose attributes from nested
    entities (using "dotted" identifiers);
 3. The view processes the order string (``order=last-name:asc``) in the same
    fashion as the query string;
 4. The view parses the batch size string (``size=100``) and applies this
    setting to the context collection resource;
 4. The view iterates over the context collection resource and wraps the
    filtered, ordered, and batched member resources into a new result
    collection resource;
 5. Using a representer, the view creates a string representation of the
    resource of the appropriate content type (either requested by the client
    or statically defined for the resource);
 6. The view fills the response body with the representation, sets up the
    response headers and returns the response for further processing through
    the WSGI stack.


As an example, querying a collection resource ""

.. code-block: text


If a query contains multiple criteria with different resource attribute names,
the criteria are interpreted as a Boolean "AND" operation.

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
    ``contains``                 x
  ``not-contains``               x
   ``contained``                 x
 ``not-contained``               x
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
that of SQL.


Customizing representations
---------------------------

The default behavior of the :mod:`everest` representers is to

 * Represent all terminal attributes explicitly;
 * Represent nested member resources as links; and
 * Ignore nested collection resources.

Nested collections are ignored by default because generating a URL for a
collection may require iterating over all its members which is potentially
a very time consuming operation.

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


Customizing resources
---------------------



Customizing views
-----------------

Very l, the standard :mod:`everest` views will
not






