=========================
``psyclone.domain.lfric``
=========================

.. automodule:: psyclone.domain.lfric

   .. contents::
      :local:


Submodules
==========

.. toctree::

   psyclone.domain.lfric.algorithm
   psyclone.domain.lfric.arg_index_to_metadata_index
   psyclone.domain.lfric.arg_ordering
   psyclone.domain.lfric.function_space
   psyclone.domain.lfric.kern_call_acc_arg_list
   psyclone.domain.lfric.kern_call_arg_list
   psyclone.domain.lfric.kern_call_invoke_arg_list
   psyclone.domain.lfric.kern_stub_arg_list
   psyclone.domain.lfric.kernel
   psyclone.domain.lfric.kernel_interface
   psyclone.domain.lfric.lfric_arg_descriptor
   psyclone.domain.lfric.lfric_builtins
   psyclone.domain.lfric.lfric_collection
   psyclone.domain.lfric.lfric_constants
   psyclone.domain.lfric.lfric_extract_driver_creator
   psyclone.domain.lfric.lfric_invoke
   psyclone.domain.lfric.lfric_kern_call_factory
   psyclone.domain.lfric.lfric_loop_bounds
   psyclone.domain.lfric.lfric_scalar_args
   psyclone.domain.lfric.lfric_symbol_table
   psyclone.domain.lfric.lfric_types
   psyclone.domain.lfric.metadata_to_arguments_rules
   psyclone.domain.lfric.transformations
   psyclone.domain.lfric.utils

.. currentmodule:: psyclone.domain.lfric


Classes
=======

- :py:class:`ArgOrdering`:
  Base class capturing the arguments, type and ordering of data in

- :py:class:`FunctionSpace`:
  Manages the name of a function space. If it is an any_space or

- :py:class:`KernCallAccArgList`:
  Kernel call arguments that need to be declared by OpenACC

- :py:class:`KernCallArgList`:
  Creates the argument list required to call kernel "kern" from the

- :py:class:`KernelInterface`:
  Create the kernel arguments for the supplied kernel as specified by

- :py:class:`KernStubArgList`:
  Creates the argument list required to create and declare the

- :py:class:`LFRicArgDescriptor`:
  This class captures the information specified in one of LFRic API argument

- :py:class:`LFRicCollection`:
  Base class for managing the declaration and initialisation of a

- :py:class:`LFRicConstants`:
  This class stores all LFRic constants. Note that some constants

- :py:class:`LFRicExtractDriverCreator`:
  This class provides the functionality to create a driver that

- :py:class:`LFRicInvoke`:
  The LFRic-specific Invoke class. This passes the LFRic-specific

- :py:class:`LFRicLoopBounds`:
  Handles all variables required for specifying loop limits within

- :py:class:`LFRicScalarArgs`:
  Handles the declarations of scalar kernel arguments appearing in either

- :py:class:`LFRicSymbolTable`:
  Sub-classes SymbolTable to provide a LFRic-specific implementation.


.. autoclass:: ArgOrdering
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: ArgOrdering
      :parts: 1

.. autoclass:: FunctionSpace
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: FunctionSpace
      :parts: 1

.. autoclass:: KernCallAccArgList
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: KernCallAccArgList
      :parts: 1

.. autoclass:: KernCallArgList
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: KernCallArgList
      :parts: 1

.. autoclass:: KernelInterface
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: KernelInterface
      :parts: 1

.. autoclass:: KernStubArgList
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: KernStubArgList
      :parts: 1

.. autoclass:: LFRicArgDescriptor
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicArgDescriptor
      :parts: 1

.. autoclass:: LFRicCollection
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicCollection
      :parts: 1

.. autoclass:: LFRicConstants
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicConstants
      :parts: 1

.. autoclass:: LFRicExtractDriverCreator
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicExtractDriverCreator
      :parts: 1

.. autoclass:: LFRicInvoke
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicInvoke
      :parts: 1

.. autoclass:: LFRicLoopBounds
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicLoopBounds
      :parts: 1

.. autoclass:: LFRicScalarArgs
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicScalarArgs
      :parts: 1

.. autoclass:: LFRicSymbolTable
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicSymbolTable
      :parts: 1
