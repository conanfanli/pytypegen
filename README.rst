

.. image:: https://travis-ci.org/conanfanli/pytypegen.svg?branch=master
   :target: https://travis-ci.org/conanfanli/pytypegen
   :alt: Build Status


.. image:: https://codecov.io/gh/conanfanli/pytypegen/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/conanfanli/pytypegen
   :alt: codecov


.. image:: https://pyup.io/repos/github/conanfanli/pytypegen/shield.svg
   :target: https://pyup.io/repos/github/conanfanli/pytypegen/shield.svg
   :alt: pyup


pytypgen
========

Code generator that converts from Python types (implemented by dataclasses) to TypeScript interfaces

Dependencies
============


* Python 3.7 (need ``dataclass``\ )

Install
=======

``pip install pytypegen``

Usage
=====

.. code-block:: python

   from pytypgen.core import contracts_to_typescript, Contract

   class Gender(Enum):
       male = 1
       female = 2


   @dataclass
   class Address(Contract):
       street: str


   @dataclass
   class Person(Contract):
       name: str
       gender: Gender
       birth_date: datetime.datetime
       addresses: Optional[List[Address]] = None

   print(contracts_to_typescript(dataclasses=[Gender, Address, Person]))

Will generate the following TypeScript code:

.. code-block:: TypeScript

   export enum Gender {
     male = 'male',
     female = 'female'
   }

   export interface Address {
     street: string
   }

   export interface Person {
     name: string
     gender: Gender
     birth_date: string
     addresses?: Array<Address>|null
   }

Development Setup
=================


* Run ``make setup``. This will setup a pre-commit hook which creates README.rst file.
* Run ``pip install -r dev-requirements.txt``\ , preferably in a virtualenv.
