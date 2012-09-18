Using :mod:`everest` applications
=================================


Querying with GET
-----------------

.. sidebar:: Collection Query Language (CQL)

   :mod:`everest` supports a custom Collection Query Language (CQL) for
   querying collection resources.

   CQL query expressions are composed of one or more query criteria separated
   by the tilde ("~") character. Each criterion consists of three parts
   separated by a colon (":") character :

   1. resource attribute name
      The name of the resource attribute to query. You can specify dotted 
      names to query nested resources.
   2. operator 
      The operator to apply.
   3. value 
      The value to query for. It is possible to supply multiple values
      in a comma separated list, which will be interpreted as a Boolean "OR"
      operation on all given values. 
      
   Supported query criterion value types are:

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

One of the main features of the collection resources in :mod:`everest` are their
advanced querying capabilities. Query strings have to conform to a simple
"Collection Query Language"

An incoming query through a GET request is processed by :mod:`everest` in three
steps:

 1. The query string submitted by the client is parsed into a resource filter
    specification and applied to the context collection resource.
 2. The resource filter specification is translated into an entity filter
    specification. This allows not only to expose entity attributes under a
    different name, but also to expose attributes from nested entities.
 3. The entity filter specification is applied to the aggregate which in
    turn performs the specified filtering operation when it is iterated.



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