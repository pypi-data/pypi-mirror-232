=========================================
``psyclone.domain.lfric.algorithm.psyir``
=========================================

.. automodule:: psyclone.domain.lfric.algorithm.psyir

   .. contents::
      :local:


Submodules
==========

.. toctree::

   psyclone.domain.lfric.algorithm.psyir.lfric_alg_invoke_call
   psyclone.domain.lfric.algorithm.psyir.lfric_kernel_functor

.. currentmodule:: psyclone.domain.lfric.algorithm.psyir


Classes
=======

- :py:class:`LFRicAlgorithmInvokeCall`:
  An invoke call from the LFRic Algorithm layer.

- :py:class:`LFRicKernelFunctor`:
  Object containing a call to a user-provided LFRic kernel, a description

- :py:class:`LFRicBuiltinFunctor`:
  Base class which all LFRic builtins subclass. Contains a builtin call,

- :py:class:`LFRicBuiltinFunctorFactory`:
  This class is a singleton which generates and stores a Functor class for


.. autoclass:: LFRicAlgorithmInvokeCall
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicAlgorithmInvokeCall
      :parts: 1

.. autoclass:: LFRicKernelFunctor
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicKernelFunctor
      :parts: 1

.. autoclass:: LFRicBuiltinFunctor
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicBuiltinFunctor
      :parts: 1

.. autoclass:: LFRicBuiltinFunctorFactory
   :members:

   .. rubric:: Inheritance
   .. inheritance-diagram:: LFRicBuiltinFunctorFactory
      :parts: 1
