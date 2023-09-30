==================
``psyclone.parse``
==================

.. automodule:: psyclone.parse

   .. contents::
      :local:


Submodules
==========

.. toctree::

   psyclone.parse.algorithm
   psyclone.parse.kernel
   psyclone.parse.module_info
   psyclone.parse.module_manager
   psyclone.parse.utils

.. currentmodule:: psyclone.parse


Classes
=======

- :py:class:`ModuleInfo`:
  This class stores mostly cached information about modules: it stores

- :py:class:`ModuleManager`:
  This class implements a singleton that manages module


.. autoclass:: ModuleInfo
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: ModuleInfo
      :parts: 1

.. autoclass:: ModuleManager
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: ModuleManager
      :parts: 1


Exceptions
==========

- :py:exc:`ModuleInfoError`:
  PSyclone-specific exception for use when an error with the module manager


.. autoexception:: ModuleInfoError

   .. rubric:: Inheritance
   .. inheritance-diagram:: ModuleInfoError
      :parts: 1
