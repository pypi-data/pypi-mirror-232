Budo Systems Software Design
============================

This document describes the design principles used to guide the development of Budo Systems.

Domain Driven Design
--------------------

The crux of the design decisions for this software center on Domain Driven Design.
Much of the initial focus has been on the model (budosystems.models package), specifically on the meta and core modules.
The idea here is that the domain model (in this case, concepts surrounding the business of running a martial arts
school) is the central piece from which all other software services derive.

From this model we can generate the database schema, the REST API, the web views, the mobile app views, etc.
Keeping the model storage-agnostic and view-agnostic means we can make the implementations pluggable.
The data can be persisted in a relational database, a document database, a graph database, a file system full of JSON
files, a giant XML file, all depending on the needs and resources of the business.
Likewise, the web views can be created with Flask, Django, Pyramid, or any other framework, or hand crafted.

Limit External Dependencies
---------------------------

For the core part of the system, I wanted to rely on as few external packages as possible.
First, see what's available in the standard Python library.
If what you need isn't there, see if it's easy to implement.
If it's not easy, then see what's available elsewhere.

For instance, the model classes are generally speaking mostly just data schemata.
I initially tried to use the `dataclasses` library, but found it too limited for what I wanted to accomplish, so I
started using the `attrs` library.

Metaprogramming is Good (In Small Doses)
----------------------------------------

This project uses meta-programming, in particular metaclasses, to make things easier and cleaner elsewhere in the code.

The `BudoMeta` class wraps all the model classes with `attr.s` with some defaults appropriate for the model.
The defaults can be overridden on a case-by-case basis at class definition.
It's a great tool supporting the *Don't Repeat Yourself* mantra.

The `SingletonMeta` class allows for quick creation of singleton classes that are type appropriate without having
to repeat the whole entire pattern.

With these examples in mind, it's important not to go overboard with this style of programming.
Don't make it a case of a solution in search of a problem.

Type Hinting, Type Checking
---------------------------

One recent addition to Python used throughout the project is type annotation.
Almost everything has type been annotated with type-hints.
Mypy is used to statically check the code for typing errors.

The Budo Systems Model
----------------------

Here's a class diagram representing the high level class structure of the domain model:

.. uml::

  hide empty members

  package budosystems.models {
      package meta {
        class BudoMeta << (M,thistle) >> {
          <&lock-locked> uuid: UUID
          <&lock-locked> config: Map<str, Any>
          <&lock-locked> metadata: Map<str, Any>
          __new__(mcs, ...)
          __init__(cls, ...)
        }

        note "Wraps all instance classes with attr.s" as BudoNote
        BudoMeta -- BudoNote

        class BudoBase <<BudoMeta>> {
          __init__(self, **kwargs)
        }

        class ABCBudoMeta  << (M,thistle) >>  extends BudoMeta, collections.abc.ABCMeta

        BudoMeta }.. BudoBase

      }
      package core {
        class Entity extends BudoBase {
          <&lock-locked> entity_id: UUID
          <&lock-locked> id_name: str
        }

        class BasicInfo extends Entity {
          <&pencil> name: str
          <&lock-locked> slug: str
          <&pencil> description: str
        }

        class ValueObject<frozen=True> extends BudoBase
      }
      package "(others)" {
        class SomeValueObject extends ValueObject {
          {field} ...
          {method} ...
        }

        together {
          class SomeModelEntity extends Entity {
            {field} ...
            {method} ...
          }

          class SomePublicFacingEntity extends BasicInfo {
            {field} ...
            {method} ...
          }

          class GenericEntity<X, Y> <<ABCBudoMeta>> extends Entity {
            {field} ...
            {method} ...
          }
        }

        ABCBudoMeta }.. GenericEntity
      }
    }

    namespace collections.abc {
      class ABCMeta << (M,thistle) >>
    }
