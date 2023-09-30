# -----------------------------------------------------------------------------
# BSD 3-Clause License
#
# Copyright (c) 2022-2023, Science and Technology Facilities Council.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------
# Author: A. R. Porter, STFC Daresbury Lab
# Modified: R. W. Ford and S. Siso, STFC Daresbury Lab
# -----------------------------------------------------------------------------

'''This module contains pytest tests for the IntrinsicCall node.'''

import pytest

from psyclone.core import VariablesAccessInfo
from psyclone.psyir.nodes import (
    ArrayReference, Literal, IntrinsicCall, Reference, Schedule, Assignment)
from psyclone.psyir.symbols import (
    ArrayType, DataSymbol, INTEGER_TYPE, IntrinsicSymbol, REAL_TYPE,
    BOOLEAN_TYPE, CHARACTER_TYPE)


def test_intrinsiccall_constructor():
    '''Tests that the class' constructor and its parent are called
    correctly.

    '''
    # Wrong type of routine argument.
    with pytest.raises(TypeError) as err:
        _ = IntrinsicCall(None)
    assert ("IntrinsicCall 'routine' argument should be an instance of "
            "IntrinsicCall.Intrinsic, but found 'NoneType'." in str(err.value))
    # Check that supplied intrinsic and optional parent node is stored
    # correctly.
    sched = Schedule()
    call = IntrinsicCall(IntrinsicCall.Intrinsic.MINVAL, parent=sched)
    assert call._intrinsic is IntrinsicCall.Intrinsic.MINVAL
    assert isinstance(call.routine, IntrinsicSymbol)
    assert call.routine.name == "MINVAL"
    assert call.parent is sched


def test_intrinsiccall_intrinsic():
    '''Tests the intrinsic property returns the type of intrinsics from
    the intrinsic property.

    '''
    call = IntrinsicCall(IntrinsicCall.Intrinsic.MAXVAL)
    assert call.intrinsic is IntrinsicCall.Intrinsic.MAXVAL


def test_intrinsiccall_is_elemental():
    '''Tests the is_elemental() method works as expected. There are
    currently no elemental intrinsics so we can only test for
    False.

    '''
    intrinsic = IntrinsicCall(IntrinsicCall.Intrinsic.SUM)
    assert intrinsic.is_elemental is False


def test_intrinsiccall_is_pure():
    '''Tests that the is_pure() method works as expected.'''
    intrinsic = IntrinsicCall(IntrinsicCall.Intrinsic.SUM)
    assert intrinsic.is_pure is True
    intrinsic = IntrinsicCall(IntrinsicCall.Intrinsic.ALLOCATE)
    assert intrinsic.is_pure is False


@pytest.mark.parametrize("intrinsic, result", [
                (IntrinsicCall.Intrinsic.ABS, True),
                (IntrinsicCall.Intrinsic.MIN, True),
                (IntrinsicCall.Intrinsic.MAX, True),
                (IntrinsicCall.Intrinsic.MAXVAL, False),
                (IntrinsicCall.Intrinsic.ALLOCATE, False),
                (IntrinsicCall.Intrinsic.MATMUL, False)])
def test_intrinsiccall_is_available_on_device(intrinsic, result):
    '''Tests that the is_available_on_device() method works as expected.'''
    intrinsic_call = IntrinsicCall(intrinsic)
    assert intrinsic_call.is_available_on_device() is result


def test_intrinsiccall_alloc_create():
    '''Tests the create() method supports various forms of 'allocate'.

    '''
    sym = DataSymbol("my_array", ArrayType(INTEGER_TYPE,
                                           [ArrayType.Extent.DEFERRED]))
    bsym = DataSymbol("my_array2", ArrayType(INTEGER_TYPE,
                                             [ArrayType.Extent.DEFERRED]))
    isym = DataSymbol("ierr", INTEGER_TYPE)
    csym = DataSymbol("msg", CHARACTER_TYPE)
    # Straightforward allocation of an array.
    alloc = IntrinsicCall.create(
        IntrinsicCall.Intrinsic.ALLOCATE,
        [ArrayReference.create(sym, [Literal("20", INTEGER_TYPE)])])
    assert isinstance(alloc, IntrinsicCall)
    assert alloc.intrinsic is IntrinsicCall.Intrinsic.ALLOCATE
    assert isinstance(alloc.routine, IntrinsicSymbol)
    assert alloc.routine.name == "ALLOCATE"
    alloc = IntrinsicCall.create(
        IntrinsicCall.Intrinsic.ALLOCATE,
        [Reference(sym), ("Mold", Reference(bsym))])
    assert isinstance(alloc, IntrinsicCall)
    assert alloc.argument_names == [None, "Mold"]
    alloc = IntrinsicCall.create(
        IntrinsicCall.Intrinsic.ALLOCATE,
        [Reference(sym), ("Source", Reference(bsym)),
         ("stat", Reference(isym)), ("errmsg", Reference(csym))])
    assert alloc.argument_names == [None, "Source", "stat", "errmsg"]


def test_intrinsiccall_dealloc_create():
    '''Tests for the creation of a 'deallocate' call.

    '''
    sym = DataSymbol("my_array", ArrayType(INTEGER_TYPE,
                                           [ArrayType.Extent.DEFERRED]))
    ierr = DataSymbol("ierr", INTEGER_TYPE)
    dealloc = IntrinsicCall.create(
        IntrinsicCall.Intrinsic.DEALLOCATE, [Reference(sym)])
    assert isinstance(dealloc, IntrinsicCall)
    assert dealloc.intrinsic is IntrinsicCall.Intrinsic.DEALLOCATE
    assert isinstance(dealloc.routine, IntrinsicSymbol)
    assert dealloc.routine.name == "DEALLOCATE"
    assert dealloc.children[0].symbol is sym
    # With 'stat' optional argument.
    dealloc = IntrinsicCall.create(
        IntrinsicCall.Intrinsic.DEALLOCATE, [Reference(sym),
                                             ("Stat", Reference(ierr))])
    assert dealloc.argument_names == [None, "Stat"]


def test_intrinsiccall_random_create():
    '''Tests for the creation of a 'random' call.

    '''
    sym = DataSymbol("my_array", ArrayType(REAL_TYPE,
                                           [ArrayType.Extent.DEFERRED]))
    rand = IntrinsicCall.create(
        IntrinsicCall.Intrinsic.RANDOM_NUMBER, [Reference(sym)])
    assert isinstance(rand, IntrinsicCall)
    assert rand.intrinsic is IntrinsicCall.Intrinsic.RANDOM_NUMBER
    assert isinstance(rand.routine, IntrinsicSymbol)
    assert rand.routine.name == "RANDOM_NUMBER"
    assert rand.children[0].symbol is sym


@pytest.mark.parametrize("intrinsic_call", [
    IntrinsicCall.Intrinsic.MINVAL, IntrinsicCall.Intrinsic.MAXVAL,
    IntrinsicCall.Intrinsic.SUM])
def test_intrinsiccall_minmaxsum_create(intrinsic_call):
    '''Tests for the creation of the different argument options for
    'minval', 'maxval' and 'sum' IntrinsicCalls.

    '''
    array = DataSymbol(
        "my_array", ArrayType(REAL_TYPE, [ArrayType.Extent.DEFERRED]))
    dim = DataSymbol("dim", INTEGER_TYPE)
    mask = DataSymbol("mask", BOOLEAN_TYPE)

    # array only
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [Reference(array)])
    assert isinstance(intrinsic, IntrinsicCall)
    assert intrinsic.intrinsic is intrinsic_call
    assert isinstance(intrinsic.routine, IntrinsicSymbol)
    intrinsic_name = intrinsic_call.name
    assert intrinsic.routine.name == intrinsic_name
    assert intrinsic.children[0].symbol is array
    # array and optional dim
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [Reference(array), ("dim", Reference(dim))])
    assert intrinsic.argument_names == [None, "dim"]
    # array and optional mask
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [Reference(array), ("mask", Reference(mask))])
    assert intrinsic.argument_names == [None, "mask"]
    # array and optional dim then optional mask
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [Reference(array), ("dim", Reference(dim)),
                         ("mask", Reference(mask))])
    assert intrinsic.argument_names == [None, "dim", "mask"]
    # array and optional mask then optional dim
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [Reference(array), ("mask", Reference(mask)),
                         ("dim", Reference(dim))])
    assert intrinsic.argument_names == [None, "mask", "dim"]
    # array and optional literal mask and optional literal dim
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [
            Reference(array),
            ("mask", Literal("1", INTEGER_TYPE)),
            ("dim", Literal("false", BOOLEAN_TYPE))])
    assert intrinsic.argument_names == [None, "mask", "dim"]


@pytest.mark.parametrize("intrinsic_call", [
    IntrinsicCall.Intrinsic.TINY, IntrinsicCall.Intrinsic.HUGE])
@pytest.mark.parametrize("form", ["array", "literal"])
def test_intrinsiccall_tinyhuge_create(intrinsic_call, form):
    '''Tests for the creation of the different argument options for
    'tiny' and 'huge' IntrinsicCalls.

    '''
    if form == "array":
        array = DataSymbol(
            "my_array", ArrayType(REAL_TYPE, [ArrayType.Extent.DEFERRED]))
        arg = Reference(array)
    else:  # "literal"
        arg = Literal("1.0", REAL_TYPE)
    intrinsic = IntrinsicCall.create(
        intrinsic_call, [arg])
    assert isinstance(intrinsic, IntrinsicCall)
    assert intrinsic.intrinsic is intrinsic_call
    assert isinstance(intrinsic.routine, IntrinsicSymbol)
    intrinsic_name = intrinsic_call.name
    assert intrinsic.routine.name == intrinsic_name
    if form == "array":
        assert intrinsic.children[0].symbol is array
    else:  # "literal"
        assert intrinsic.children[0] is arg


def test_intrinsiccall_create_errors():
    '''Checks for the validation/type checking in the create() method.

    '''
    sym = DataSymbol("my_array", ArrayType(INTEGER_TYPE,
                                           [ArrayType.Extent.DEFERRED]))
    aref = ArrayReference.create(sym, [Literal("20", INTEGER_TYPE)])
    with pytest.raises(TypeError) as err:
        IntrinsicCall.create("ALLOCATE", [Reference(sym)])
    assert ("'routine' argument should be an instance of "
            "IntrinsicCall.Intrinsic but found 'str'" in str(err.value))
    # Supplied arguments must be a list.
    with pytest.raises(TypeError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.ALLOCATE, aref)
    assert ("IntrinsicCall.create() 'arguments' argument should be a list "
            "but found 'ArrayReference'" in str(err.value))
    # An allocate must have one or more References as argument.
    with pytest.raises(ValueError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.ALLOCATE, [])
    assert ("The 'ALLOCATE' intrinsic requires at least 1 arguments but "
            "got 0" in str(err.value))
    # The random intrinsic only accepts one argument.
    with pytest.raises(ValueError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.RANDOM_NUMBER,
                             [aref, aref.copy()])
    assert ("The 'RANDOM_NUMBER' intrinsic requires between 1 and 1 arguments "
            "but got 2" in str(err.value))
    # Wrong type for a positional argument.
    with pytest.raises(TypeError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.ALLOCATE,
                             [sym])
    assert ("The 'ALLOCATE' intrinsic requires that positional arguments be "
            "of type " in str(err.value))
    assert "but got a 'DataSymbol'" in str(err.value)
    # Positional argument after named argument.
    with pytest.raises(ValueError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.DEALLOCATE,
                             [Reference(sym), ("stat", aref), aref])
    assert ("Found a positional argument *after* a named argument ('stat'). "
            "This is invalid." in str(err.value))

    # TODO #2303: We can not enable the validation of positional parameters
    # unless we store their name, otherwise when we parse a positional argument
    # by name, which is valid fortran, it will fail.
    # (e.g. RANDOM_NUMBER(harvest=4)

    # with pytest.raises(ValueError) as err:
    #     IntrinsicCall.create(IntrinsicCall.Intrinsic.RANDOM_NUMBER,
    #                          [aref, ("willow", sym)])
    # assert ("The 'RANDOM_NUMBER' intrinsic does not support any optional "
    #         "arguments but got 'willow'" in str(err.value))
    # An allocate only supports the 'stat' and 'mold' arguments.
    # with pytest.raises(ValueError) as err:
    #     IntrinsicCall.create(IntrinsicCall.Intrinsic.ALLOCATE,
    #                          [aref, ("yacht", Reference(sym))])
    # assert ("The 'ALLOCATE' intrinsic supports the optional arguments "
    #         "['errmsg', 'mold', 'source', 'stat'] but got 'yacht'"
    #         in str(err.value))

    # Wrong type for the name of an optional argument.
    with pytest.raises(TypeError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.ALLOCATE,
                             [aref, (sym, sym)])
    assert ("Optional arguments to an IntrinsicCall must be specified by a "
            "(str, Reference) tuple but got a DataSymbol instead of a str"
            in str(err.value))
    # Wrong type for an optional argument.
    with pytest.raises(TypeError) as err:
        IntrinsicCall.create(IntrinsicCall.Intrinsic.ALLOCATE,
                             [aref, ("stat", sym)])
    assert ("The optional argument 'stat' to intrinsic 'ALLOCATE' must be "
            "of type 'Reference' but got 'DataSymbol'" in str(err.value))


def test_create_positional_arguments_with_names():
    ''' Test the create method when given named positional arguments.'''
    sym = DataSymbol("my_array",
                     ArrayType(INTEGER_TYPE, [ArrayType.Extent.DEFERRED]))
    aref = ArrayReference.create(sym, [Literal("20", INTEGER_TYPE)])
    bref = ArrayReference.create(sym, [Literal("20", INTEGER_TYPE)])

    # All of these are valid
    intr = IntrinsicCall.create(IntrinsicCall.Intrinsic.DOT_PRODUCT,
                                [aref.copy(), bref.copy()])
    assert isinstance(intr, IntrinsicCall)
    assert intr.children[0] == aref
    assert intr.children[1] == bref
    assert intr.argument_names == [None, None]

    intr = IntrinsicCall.create(IntrinsicCall.Intrinsic.DOT_PRODUCT,
                                [aref.copy(), ("vector_b", bref.copy())])
    assert isinstance(intr, IntrinsicCall)
    assert intr.children[0] == aref
    assert intr.children[1] == bref
    assert intr.argument_names == [None, "vector_b"]

    intr = IntrinsicCall.create(IntrinsicCall.Intrinsic.DOT_PRODUCT,
                                [("vector_a", aref.copy()),
                                 ("vector_b", bref.copy())])
    assert isinstance(intr, IntrinsicCall)
    assert intr.children[0] == aref
    assert intr.children[1] == bref
    assert intr.argument_names == ["vector_a", "vector_b"]

    intr = IntrinsicCall.create(IntrinsicCall.Intrinsic.DOT_PRODUCT,
                                [("vector_b", bref.copy()),
                                 ("vector_a", aref.copy())])
    assert isinstance(intr, IntrinsicCall)
    assert intr.children[0] == bref
    assert intr.children[1] == aref
    assert intr.argument_names == ["vector_b", "vector_a"]


@pytest.mark.parametrize("operator", ["lbound", "ubound", "size"])
def test_reference_accesses_bounds(operator, fortran_reader):
    '''Test that the reference_accesses method behaves as expected when
    the reference is the first argument to either the lbound or ubound
    intrinsic as that is simply looking up the array bounds (therefore
    var_access_info should be empty) and when the reference is the
    second argument of either the lbound or ubound intrinsic (in which
    case the access should be a read).

    '''
    code = f'''module test
        contains
        subroutine tmp()
          real, dimension(:,:), allocatable:: a, b
          integer :: n
          n = {operator}(a, b(1,1))
        end subroutine tmp
        end module test'''
    psyir = fortran_reader.psyir_from_source(code)
    schedule = psyir.walk(Assignment)[0]

    # By default, the access to 'a' should not be reported as read,
    # but the access to b must be reported:
    vai = VariablesAccessInfo(schedule)
    assert str(vai) == "b: READ, n: WRITE"

    # When explicitly requested, the access to 'a' should be reported:
    vai = VariablesAccessInfo(schedule,
                              options={"COLLECT-ARRAY-SHAPE-READS": True})
    assert str(vai) == "a: READ, b: READ, n: WRITE"
