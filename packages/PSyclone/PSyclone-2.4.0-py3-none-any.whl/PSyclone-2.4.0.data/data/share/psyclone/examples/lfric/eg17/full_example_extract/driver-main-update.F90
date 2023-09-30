! ================================================== !
! THIS FILE IS CREATED FROM THE JINJA TEMPLATE FILE. !
! DO NOT MODIFY DIRECTLY!                            !
! ================================================== !



! -----------------------------------------------------------------------------
! BSD 3-Clause License
!
! Copyright (c) 2022-2023, Science and Technology Facilities Council.
! All rights reserved.
!
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
!
! * Redistributions of source code must retain the above copyright notice, this
!   list of conditions and the following disclaimer.
!
! * Redistributions in binary form must reproduce the above copyright notice,
!   this list of conditions and the following disclaimer in the documentation
!   and/or other materials provided with the distribution.
!
! * Neither the name of the copyright holder nor the names of its
!   contributors may be used to endorse or promote products derived from
!   this software without specific prior written permission.
!
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
! "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
! LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
! FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
! COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
! INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
! BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
! LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
! CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
! LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
! ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
! POSSIBILITY OF SUCH DAMAGE.
! -----------------------------------------------------------------------------
! Author: J. Henrichs, Bureau of Meteorology

!> This module implements a simple binary file reader. It provides the
!! functions:
!! OpenRead:      opens a file for reading
!! ReadScalar...:           reads the specified scalar value
!! ReadArray1dDouble, ... : allocates and reads the specified array type.

module read_kernel_data_mod

    use, intrinsic :: iso_fortran_env, only : int64, int32,   &
                                              real32, real64, &
                                              stderr => Error_Unit

    implicit none

    !> This is the data type that manages the information required
    !! to read data from a Fortran binary file created by the
    !! extraction library.

    type, public :: ReadKernelDataType

        !> The unit number to use for output
        integer :: unit_number

    contains

        ! The various procedures used
        procedure :: OpenRead

        procedure :: ReadScalarChar
        procedure :: ReadArray1dChar
        procedure :: ReadArray2dChar
        procedure :: ReadArray3dChar
        procedure :: ReadArray4dChar
        procedure :: ReadScalarInt
        procedure :: ReadArray1dInt
        procedure :: ReadArray2dInt
        procedure :: ReadArray3dInt
        procedure :: ReadArray4dInt
        procedure :: ReadScalarLong
        procedure :: ReadArray1dLong
        procedure :: ReadArray2dLong
        procedure :: ReadArray3dLong
        procedure :: ReadArray4dLong
        procedure :: ReadScalarLogical
        procedure :: ReadArray1dLogical
        procedure :: ReadArray2dLogical
        procedure :: ReadArray3dLogical
        procedure :: ReadArray4dLogical
        procedure :: ReadScalarReal
        procedure :: ReadArray1dReal
        procedure :: ReadArray2dReal
        procedure :: ReadArray3dReal
        procedure :: ReadArray4dReal
        procedure :: ReadScalarDouble
        procedure :: ReadArray1dDouble
        procedure :: ReadArray2dDouble
        procedure :: ReadArray3dDouble
        procedure :: ReadArray4dDouble

        !> The generic interface for reading the value of variables.
        !! This is not part of the official PSyData API, but is used in
        !! the drivers created by PSyclone.
        generic, public :: ReadVariable => &
            ReadScalarChar, &
            ReadArray1dChar, &
            ReadArray2dChar, &
            ReadArray3dChar, &
            ReadArray4dChar, &
            ReadScalarInt, &
            ReadArray1dInt, &
            ReadArray2dInt, &
            ReadArray3dInt, &
            ReadArray4dInt, &
            ReadScalarLong, &
            ReadArray1dLong, &
            ReadArray2dLong, &
            ReadArray3dLong, &
            ReadArray4dLong, &
            ReadScalarLogical, &
            ReadArray1dLogical, &
            ReadArray2dLogical, &
            ReadArray3dLogical, &
            ReadArray4dLogical, &
            ReadScalarReal, &
            ReadArray1dReal, &
            ReadArray2dReal, &
            ReadArray3dReal, &
            ReadArray4dReal, &
            ReadScalarDouble, &
            ReadArray1dDouble, &
            ReadArray2dDouble, &
            ReadArray3dDouble, &
            ReadArray4dDouble

    end type ReadKernelDataType

contains

    ! -------------------------------------------------------------------------
    !> @brief This subroutine is called to open a binary file for reading. The
    !! filename is based on the module and kernel name. This is used by a
    !! driver program that will read a binary file previously created by the
    !! PSyData API.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] module_name The name of the module of the instrumented
    !!            region.
    !! @param[in] region_name The name of the instrumented region.
    subroutine OpenRead(this, module_name, region_name)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: module_name, &
                                                         region_name
        integer :: retval

        open(newunit=this%unit_number, access='sequential',  &
             form="unformatted", status="old",               &
             file=module_name//"-"//region_name//".binary")

    end subroutine OpenRead


    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the value of a scalar character(*)
    !! variable from the binary file and returns it to the user. Note that
    !! this function is not part of the PSyData API, but it is convenient to
    !! have these functions together here. The driver can then be linked with
    !! this PSyData library and will be able to read the files.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value The read value is stored here.
    subroutine ReadScalarChar(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: name
        character(*), intent(out)                            :: value

        integer                                          :: retval, varid

        read(this%unit_number) value

    end subroutine ReadScalarChar



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 1D array of character(*)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray1dChar(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        character(*), dimension(:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1, &
                            " in ReadArray1dChar."
            stop
        endif

        ! Initialise it with "", so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = ""
        read(this%unit_number) value

    end subroutine ReadArray1dChar



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 2D array of character(*)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray2dChar(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        character(*), dimension(:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2, &
                            " in ReadArray2dChar."
            stop
        endif

        ! Initialise it with "", so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = ""
        read(this%unit_number) value

    end subroutine ReadArray2dChar



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 3D array of character(*)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray3dChar(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        character(*), dimension(:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3, &
                            " in ReadArray3dChar."
            stop
        endif

        ! Initialise it with "", so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = ""
        read(this%unit_number) value

    end subroutine ReadArray3dChar



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 4D array of character(*)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray4dChar(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        character(*), dimension(:,:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3,dim_size4
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3
        read(this%unit_number) dim_size4

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3,dim_size4), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3,dim_size4, &
                            " in ReadArray4dChar."
            stop
        endif

        ! Initialise it with "", so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = ""
        read(this%unit_number) value

    end subroutine ReadArray4dChar


    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the value of a scalar integer(kind=int32)
    !! variable from the binary file and returns it to the user. Note that
    !! this function is not part of the PSyData API, but it is convenient to
    !! have these functions together here. The driver can then be linked with
    !! this PSyData library and will be able to read the files.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value The read value is stored here.
    subroutine ReadScalarInt(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: name
        integer(kind=int32), intent(out)                            :: value

        integer                                          :: retval, varid

        read(this%unit_number) value

    end subroutine ReadScalarInt



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 1D array of integer(kind=int32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray1dInt(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int32), dimension(:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1, &
                            " in ReadArray1dInt."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray1dInt



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 2D array of integer(kind=int32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray2dInt(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int32), dimension(:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2, &
                            " in ReadArray2dInt."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray2dInt



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 3D array of integer(kind=int32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray3dInt(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int32), dimension(:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3, &
                            " in ReadArray3dInt."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray3dInt



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 4D array of integer(kind=int32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray4dInt(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int32), dimension(:,:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3,dim_size4
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3
        read(this%unit_number) dim_size4

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3,dim_size4), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3,dim_size4, &
                            " in ReadArray4dInt."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray4dInt


    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the value of a scalar integer(kind=int64)
    !! variable from the binary file and returns it to the user. Note that
    !! this function is not part of the PSyData API, but it is convenient to
    !! have these functions together here. The driver can then be linked with
    !! this PSyData library and will be able to read the files.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value The read value is stored here.
    subroutine ReadScalarLong(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: name
        integer(kind=int64), intent(out)                            :: value

        integer                                          :: retval, varid

        read(this%unit_number) value

    end subroutine ReadScalarLong



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 1D array of integer(kind=int64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray1dLong(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int64), dimension(:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1, &
                            " in ReadArray1dLong."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray1dLong



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 2D array of integer(kind=int64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray2dLong(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int64), dimension(:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2, &
                            " in ReadArray2dLong."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray2dLong



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 3D array of integer(kind=int64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray3dLong(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int64), dimension(:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3, &
                            " in ReadArray3dLong."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray3dLong



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 4D array of integer(kind=int64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray4dLong(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        integer(kind=int64), dimension(:,:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3,dim_size4
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3
        read(this%unit_number) dim_size4

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3,dim_size4), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3,dim_size4, &
                            " in ReadArray4dLong."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray4dLong


    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the value of a scalar Logical(kind=4)
    !! variable from the binary file and returns it to the user. Note that
    !! this function is not part of the PSyData API, but it is convenient to
    !! have these functions together here. The driver can then be linked with
    !! this PSyData library and will be able to read the files.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value The read value is stored here.
    subroutine ReadScalarLogical(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: name
        Logical(kind=4), intent(out)                            :: value

        integer                                          :: retval, varid

        read(this%unit_number) value

    end subroutine ReadScalarLogical



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 1D array of Logical(kind=4)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray1dLogical(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        Logical(kind=4), dimension(:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1, &
                            " in ReadArray1dLogical."
            stop
        endif

        ! Initialise it with false, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = .false.
        read(this%unit_number) value

    end subroutine ReadArray1dLogical



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 2D array of Logical(kind=4)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray2dLogical(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        Logical(kind=4), dimension(:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2, &
                            " in ReadArray2dLogical."
            stop
        endif

        ! Initialise it with false, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = .false.
        read(this%unit_number) value

    end subroutine ReadArray2dLogical



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 3D array of Logical(kind=4)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray3dLogical(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        Logical(kind=4), dimension(:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3, &
                            " in ReadArray3dLogical."
            stop
        endif

        ! Initialise it with false, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = .false.
        read(this%unit_number) value

    end subroutine ReadArray3dLogical



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 4D array of Logical(kind=4)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray4dLogical(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        Logical(kind=4), dimension(:,:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3,dim_size4
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3
        read(this%unit_number) dim_size4

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3,dim_size4), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3,dim_size4, &
                            " in ReadArray4dLogical."
            stop
        endif

        ! Initialise it with false, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all.
        value = .false.
        read(this%unit_number) value

    end subroutine ReadArray4dLogical


    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the value of a scalar real(kind=real32)
    !! variable from the binary file and returns it to the user. Note that
    !! this function is not part of the PSyData API, but it is convenient to
    !! have these functions together here. The driver can then be linked with
    !! this PSyData library and will be able to read the files.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value The read value is stored here.
    subroutine ReadScalarReal(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: name
        real(kind=real32), intent(out)                            :: value

        integer                                          :: retval, varid

        read(this%unit_number) value

    end subroutine ReadScalarReal



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 1D array of real(kind=real32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray1dReal(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real32), dimension(:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1, &
                            " in ReadArray1dReal."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray1dReal



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 2D array of real(kind=real32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray2dReal(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real32), dimension(:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2, &
                            " in ReadArray2dReal."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray2dReal



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 3D array of real(kind=real32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray3dReal(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real32), dimension(:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3, &
                            " in ReadArray3dReal."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray3dReal



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 4D array of real(kind=real32)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray4dReal(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real32), dimension(:,:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3,dim_size4
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3
        read(this%unit_number) dim_size4

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3,dim_size4), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3,dim_size4, &
                            " in ReadArray4dReal."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray4dReal


    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the value of a scalar real(kind=real64)
    !! variable from the binary file and returns it to the user. Note that
    !! this function is not part of the PSyData API, but it is convenient to
    !! have these functions together here. The driver can then be linked with
    !! this PSyData library and will be able to read the files.
    !! @param[in,out] this The instance of the ReadKernelDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value The read value is stored here.
    subroutine ReadScalarDouble(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target :: this
        character(*), intent(in)                         :: name
        real(kind=real64), intent(out)                            :: value

        integer                                          :: retval, varid

        read(this%unit_number) value

    end subroutine ReadScalarDouble



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 1D array of real(kind=real64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray1dDouble(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real64), dimension(:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1, &
                            " in ReadArray1dDouble."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray1dDouble



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 2D array of real(kind=real64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray2dDouble(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real64), dimension(:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2, &
                            " in ReadArray2dDouble."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray2dDouble



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 3D array of real(kind=real64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray3dDouble(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real64), dimension(:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3, &
                            " in ReadArray3dDouble."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray3dDouble



    ! -------------------------------------------------------------------------
    !> @brief This subroutine reads the values of a 4D array of real(kind=real64)
    !! It allocates memory for the allocatable parameter 'value' to store the
    !! read values which is then returned to the caller. If the memory for the
    !! array cannot be allocated, the application will be stopped.
    !! @param[in,out] this The instance of the extract_PsyDataType.
    !! @param[in] name The name of the variable (string).
    !! @param[out] value An allocatable, unallocated 2d-double precision array
    !!             which is allocated here and stores the values read.
    subroutine ReadArray4dDouble(this, name, value)

        implicit none

        class(ReadKernelDataType), intent(inout), target             :: this
        character(*), intent(in)                                     :: name
        real(kind=real64), dimension(:,:,:,:), allocatable, intent(out) :: value

        integer        :: retval, varid
        integer        :: dim_id
        integer        :: dim_size1,dim_size2,dim_size3,dim_size4
        integer        :: ierr

        ! First read in the sizes:
        read(this%unit_number) dim_size1
        read(this%unit_number) dim_size2
        read(this%unit_number) dim_size3
        read(this%unit_number) dim_size4

        ! Allocate enough space to store the values to be read:
        allocate(value(dim_size1,dim_size2,dim_size3,dim_size4), Stat=ierr)
        if (ierr /= 0) then
            write(stderr,*) "Cannot allocate array for ", name, &
                            " of size ", dim_size1,dim_size2,dim_size3,dim_size4, &
                            " in ReadArray4dDouble."
            stop
        endif

        ! Initialise it with 0.0d0, so that an array comparison will work
        ! even though e.g. boundary areas or so might not be set at all. Note
        ! that the compiler will convert the double precision value to the right
        ! type (e.g. int or single precision).
        value = 0.0d0
        read(this%unit_number) value

    end subroutine ReadArray4dDouble


end module read_kernel_data_mod



!-----------------------------------------------------------------------------
! Copyright (c) 2017,  Met Office, on behalf of HMSO and Queen's Printer
! For further details please refer to the file LICENCE.original which you
! should have received as part of this distribution.
!-----------------------------------------------------------------------------
! LICENCE.original is available from the Met Office Science Repository Service:
! https://code.metoffice.gov.uk/trac/lfric/browser/LFRic/trunk/LICENCE.original
!-----------------------------------------------------------------------------
! BSD 3-Clause License
!
! Modifications copyright (c) 2017-2023, Science and Technology Facilities
! Council
! All rights reserved.
!
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
!
! * Redistributions of source code must retain the above copyright notice, this
!   list of conditions and the following disclaimer.
!
! * Redistributions in binary form must reproduce the above copyright notice,
!   this list of conditions and the following disclaimer in the documentation
!   and/or other materials provided with the distribution.
!
! * Neither the name of the copyright holder nor the names of its
!   contributors may be used to endorse or promote products derived from
!   this software without specific prior written permission.
!
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
! AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
! IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
! FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
! DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
! SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
! CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
! OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
! OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! -----------------------------------------------------------------------------
!
!> @brief Define various constants for the application.
!>
!> @details Various computational, physical and geometrical constants are
!>          defined in this module. Their values are also set here.
module constants_mod

  use, intrinsic :: iso_fortran_env, only : int8, int16, int32, int64, &
                                            real32, real64, real128

  implicit none

  private

  public :: c_def, c_native,                                             &
            dp_native, dp_xios,                                          &
            i_byte, i_def, i_halo_index, i_long, i_medium, i_native,     &
            i_timestep, i_um, i_ncdf,                                    &
            l_def, l_native,                                             &
            r_def, r_double, r_ncdf, r_native, r_second, r_single, r_um, &
            r_solver, r_tran, r_bl, r_phys,                              &
            CMDI, UNSET_KEY, EMDI, IMDI, RMDI,                           &
            real_type, r_solver_real_type, r_tran_real_type,             &
            r_bl_real_type, r_phys_real_type,                            &
            integer_type, logical_type,                                  &
            EPS, tiny_eps,                                               &
            str_def, str_long, str_max_filename, str_short,              &
            str_longlong,                                                &
            LARGE_REAL_NEGATIVE, LARGE_REAL_POSITIVE,                    &
            xios_max_int, PI, degrees_to_radians, radians_to_degrees,    &
            cache_block, PRECISION_REAL, PRECISION_R_SOLVER,             &
            PRECISION_R_TRAN, EPS_R_TRAN,                                &
            PRECISION_R_BL, PRECISION_R_PHYS

  ! Define default application-defined kinds for all intrinsic data types

  !> @name Set up default kinds for real and double-precision variables.
  !> @{
  real               :: r_val              !< A native real used to compute kind of native real.
  double precision   :: dp_val             !< A native double-precision used to compute kind of native dp.

  ! Default real kind for application.







  integer,      parameter :: r_def = real64
  character(3), parameter :: PRECISION_REAL = '64'


  ! Default real kind for r_solver.







  integer,      parameter :: r_solver = real64
  character(3), parameter :: PRECISION_R_SOLVER = '64'


  ! Default real kind for r_tran.







  integer,      parameter :: r_tran = real64
  character(3), parameter :: PRECISION_R_TRAN = '64'


  ! Default real kind for r_bl.




  integer,      parameter :: r_bl = real64
  character(3), parameter :: PRECISION_R_BL = '64'


  ! Default real kind for r_phys.




  integer,      parameter :: r_phys = real64
  character(3), parameter :: PRECISION_R_PHYS = '64'


  integer, parameter :: real_type          = 1 !< A parameter used to indicate a real data typa
  integer, parameter :: r_solver_real_type = 1 !< A parameter used to indicate a r_solver data type
  integer, parameter :: r_tran_real_type   = 1 !< A parameter used to indicate a r_tran data type
  integer, parameter :: r_bl_real_type     = 1 !< A parameter used to indicate a r_bl data type
  integer, parameter :: r_phys_real_type   = 1 !< A parameter used to indicate a r_phys data type
  integer, parameter :: integer_type       = 2 !< A parameter used to indicate an integer data type
  integer, parameter :: logical_type       = 3 !< A parameter used to indicate a logical data type

  integer, parameter :: r_double = real64 !< Default double precision real kind for application.
  integer, parameter :: r_native = kind(r_val)  !< Native kind for real.
  integer, parameter :: r_ncdf   = real64 !< Default real kind used in netcdf get and put.
  integer, parameter :: r_quad   = real128 !< Default quad precision real kind for application.
  integer, parameter :: r_second = real64 !< Kind for second counts.
  integer, parameter :: r_single = real32 !< Default single precision real kind for application.
  integer, parameter :: r_um     = real64 !< Default real kind used by the UM.

  integer, parameter :: dp_native = kind(dp_val) !< Native kind for double precision.
  ! Define kinds specifically for IO
  integer, parameter :: dp_xios   = kind(dp_val) !< XIOS kind for double precision fields

  !> @}

  !> @name Complex
  !> @{
  !> @}

  !> @name Set up default kinds for integers.
  !> @{
  integer            :: i_val                      !< A native integer used to compute kind of native integer.

  integer, parameter :: i_byte       = int8        !< Explicit byte integer.
  integer, parameter :: i_def        = int32       !< Default integer kind for application.
  integer, parameter :: i_halo_index = int64       !< Integer kind for the index used in halo swapping
  integer, parameter :: i_long       = int64       !< Explicit long integer.
  integer, parameter :: i_medium     = int32       !< Explicit midsize integer.
  integer, parameter :: i_native     = kind(i_val) !< Native kind for integer.
  integer, parameter :: i_ncdf       = int32       !< Default int kind used in netcdf get and put.
  integer, parameter :: i_short      = int16       !< Explicit short integer.
  integer, parameter :: i_timestep   = int32       !< Kind for timestep counts.
  integer, parameter :: i_um         = int32       !< Default integer kind used by the UM.
  !> @}

  !> @name Set up default kinds for logicals.
  !> @{
  logical            :: l_val                   !< A native logical used to compute kind of native logical.

  integer, parameter :: l_def     = kind(l_val) !< Default logical kind for application.
  integer, parameter :: l_native  = kind(l_val) !< Native kind for logical.
  !> @}

  !> @name Set up default kinds for character variables.
  !> @{
  character          :: c_val                   !< A native character used to compute kind of native character.

  integer, parameter :: c_def     = kind(c_val) !< Default character kind for application.
  integer, parameter :: c_native  = kind(c_val) !< Native kind for character.
  !> @}

  !> @name Set up default lengths for string variables.
  !> @{
  integer, parameter :: str_short        = 16  !< Length of "short" strings.
  integer, parameter :: str_def          = 128 !< Default string length for normal strings.
  integer, parameter :: str_long         = 255 !< Default length of long string.
  integer, parameter :: str_longlong     = 512 !< Default length of longer string.
  integer, parameter :: str_max_filename = 512 !< Default maximum length of a file-name.
  !> @}

  !> @name Platform constants
  !> @{
  real(kind=r_def), parameter    :: LARGE_REAL_POSITIVE = huge(0.0_r_def) !< The largest
  !<                                positive number of kind r_def that is not an infinity.
  real(kind=r_def), parameter    :: LARGE_REAL_NEGATIVE = -LARGE_REAL_POSITIVE !< The largest
  !<                                negative number of kind r_def that is not an infinity.

  integer(kind=i_def), parameter :: xios_max_int = huge(0_i_short) !< The largest
  !<                                integer that can be output by XIOS
  integer, parameter :: cache_block = 256 !< Size of a cache block, for padding
  !<                                arrays to ensure access to different cache lines

  !> @}

  !> @name Numerical constants
  !> @{
  real(kind=r_def), parameter  :: EPS = 3.0e-15_r_def
  !<                              Relative precision: if (abs(x-y) < EPS) then assume x==y.
  real(kind=r_tran), parameter :: EPS_R_TRAN = 3.0e-15_r_def
  !<                              Relative precision: if (abs(x-y) < EPS_R_TRAN) then assume x==y.
  real(kind=r_tran), parameter :: tiny_eps = 1.0e-30_r_tran
  !<                              Similar to EPS but lot smaller, which can be used where
  !<                              x/y < EPS but (x-y) is not considered to be zero like many chemistry tracers.
  !> @}

  !> @name Mathematical constants
  !> @{
  real(kind=r_def), parameter :: PI  = 4.0_r_def*atan(1.0_r_def) !< Value of pi.
  !> @}

  !> @name Conversion factors
  !> @{
  real(r_def), parameter :: degrees_to_radians = PI / 180.0_r_def
  real(r_def), parameter :: radians_to_degrees = 180.0_r_def / PI

  !> @}
  ! Missing data indicators
  real     (r_def),     parameter :: RMDI  = -huge(0.0_r_def) !< Value for real numbers
  integer  (i_def),     parameter :: IMDI  = -huge(0_i_def)   !< Value for integer numbers
  character(str_short), parameter :: CMDI  = 'unset'          !< Value for characters
  character(str_short), parameter :: UNSET_KEY  = CMDI        !< Chararater value for namelist enumerations
  integer  (i_native),  parameter :: EMDI  = -1_i_native      !< Integer value for namelist enumerations

  !> @}

end module constants_mod



!-----------------------------------------------------------------------------
! Copyright (c) 2017,  Met Office, on behalf of HMSO and Queen's Printer
! For further details please refer to the file LICENCE.original which you
! should have received as part of this distribution.
!-----------------------------------------------------------------------------
! LICENCE.original is available from the Met Office Science Repository Service:
! https://code.metoffice.gov.uk/trac/lfric/browser/LFRic/trunk/LICENCE.original
!-----------------------------------------------------------------------------

!-----------------------------------------------------------------------------
! BSD 3-Clause License
!
! Modifications copyright (c) 2020-2021, Science and Technology
! Facilities Council.
! All rights reserved.
!
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
!
! * Redistributions of source code must retain the above copyright notice, this
!   list of conditions and the following disclaimer.
!
! * Redistributions in binary form must reproduce the above copyright notice,
!   this list of conditions and the following disclaimer in the documentation
!   and/or other materials provided with the distribution.
!
! * Neither the name of the copyright holder nor the names of its
!   contributors may be used to endorse or promote products derived from
!   this software without specific prior written permission.
!
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
! AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
! IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
! FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
! DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
! SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
! CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
! OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
! OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! -----------------------------------------------------------------------------
!
! Modified I. Kavcic and A. Coughtrie, Met Office
!          A. R. Porter and R. W. Ford, STFC Daresbury Laboratory


!> @brief Metadata for the kernel arguments required by the PSy layer.

!> @details In order to create the correct PSy code, PSyclone requires several
!!          kernel argument properties. These properties are stored in kernels
!!          as the kernel metadata descriptors (see PSyclone documentation:
!!          https://psyclone.readthedocs.io/en/stable/dynamo0p3.html#metadata).
!!          The elements of PSyclone LFRic API kernel metadata are:
!!
!!          1) `type(arg_type) :: meta_args(...)` that describes properties of
!!             kernel arguments (e.g.\ argument type, access);
!!
!!          2) `type(func_type) :: meta_funcs(...)` that describes the required
!!             basis/differential basis functions information;
!!
!!          3) `type(reference_element_data_type) :: meta_reference_element(...`
!!             that describes the required reference element properties
!!             information;
!!
!!          4) `type(mesh_data_type) :: meta_mesh(...)` that describes the
!!             required mesh properties information;
!!
!!          5) `gh_shape = ...` (e.g.\ `gh_shape = gh_quadrature_XYoZ` that
!!             describes the required quadrature and/or evaluator properties
!!             information;
!!
!!          6) `operates_on` metadata that describes what the kernel updates,
!!             e.g.\ a vertical single-cell column;
!!
!!          7) `procedure` metadata that specifies the name of the kernel
!!             subroutine that the metadata describes.
!!
!!          `type(arg_type) :: meta_args(...)`, `operates_on` and
!!          the `procedure` metadata are mandatory for all kernels.
module argument_mod

  implicit none

  private

  !> @defgroup argument_type Enumeration of argument type property descriptors.
  !> @{
  integer, public, parameter :: GH_SCALAR              = 397
  integer, public, parameter :: GH_FIELD               = 507
  integer, public, parameter :: GH_OPERATOR            = 735
  integer, public, parameter :: GH_COLUMNWISE_OPERATOR = 841
  !> @}

  !> @defgroup data_type Enumeration of argument data type property descriptors.
  !> @{
  integer, public, parameter :: GH_REAL    = 58
  integer, public, parameter :: GH_INTEGER = 5
  integer, public, parameter :: GH_LOGICAL = 987
  !> @}

  !> @defgroup argument_access Enumeration of argument access property descriptors.
  !> @{
  integer, public, parameter :: GH_READ      = 958
  integer, public, parameter :: GH_WRITE     = 65
  integer, public, parameter :: GH_READWRITE = 811
  integer, public, parameter :: GH_INC       = 542
  integer, public, parameter :: GH_READINC   = 420
  integer, public, parameter :: GH_SUM       = 563
  integer, public, parameter :: GH_MIN       = 718
  integer, public, parameter :: GH_MAX       = 391
  !> @}

  !> @defgroup fspace Enumeration of function space IDs (also "fspace_from").
  !> @details This module defines three types of generalised function space IDs:
  !!          1) "ANY_SPACE_[1-10]+" for generalised function spaces regardless
  !!              of their continuity;
  !!          2) "ANY_W2" for any `W2`-type space regardless of its continuity;
  !!          3) "ANY_DISCONTINUOUS_SPACE_[1-10]+" for generalised discontinuous
  !!             function spaces.
  !!          Distinct IDs are required as we may have groups of fields that
  !!          must be on the same space within a kernel.
  !! @{
  ! IDs for any space regardless of continuity.
  integer, public, parameter :: ANY_SPACE_1    = 368
  integer, public, parameter :: ANY_SPACE_2    = 389
  integer, public, parameter :: ANY_SPACE_3    = 194
  integer, public, parameter :: ANY_SPACE_4    = 816
  integer, public, parameter :: ANY_SPACE_5    = 461
  integer, public, parameter :: ANY_SPACE_6    = 734
  integer, public, parameter :: ANY_SPACE_7    = 890
  integer, public, parameter :: ANY_SPACE_8    = 74
  integer, public, parameter :: ANY_SPACE_9    = 922
  integer, public, parameter :: ANY_SPACE_10   = 790
  ! IDs for any W2-type space regardless of continuity
  ! (w2, w2h, w2v, w2broken but not w2*trace spaces of scalar
  ! functions). Issue #540 will resolve what W2* spaces should
  ! be included in ANY_W2 list and how they should be treated.
  integer, public, parameter :: ANY_W2         = 353
  ! IDs for any discontinuous space.
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_1  = 43
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_2  = 711
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_3  = 267
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_4  = 901
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_5  = 174
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_6  = 683
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_7  = 425
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_8  = 361
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_9  = 536
  integer, public, parameter :: ANY_DISCONTINUOUS_SPACE_10 = 882
  !> @}

  !> @defgroup stencil_map Enumeration of stencil access map types.
  !> @{
  integer, public, parameter :: XORY1D  = 1
  integer, public, parameter :: X1D     = 2
  integer, public, parameter :: Y1D     = 3
  integer, public, parameter :: CROSS   = 4
  integer, public, parameter :: REGION  = 5
  integer, public, parameter :: CROSS2D = 6
  !> @}

  !> Allows metadata types to be syntactically correct.
  !>
  !> This is a dummy array which the enumerators can index. It is not a real
  !! thing (it is just there to ensure the compiler is happy).
  !>
  !> @todo In an ideal world this would be implemented as a function which
  !!       would remove the need for 1-based enumerator values but
  !!       GFortran doesn't like that.
  integer, public, parameter :: STENCIL(6) = -1

  !> @defgroup mesh_arg Enumeration of coarse and fine function spaces
  !>                    for inter-grid mapping kernels.
  !> @{
  integer, public, parameter :: GH_FINE   = 27745
  integer, public, parameter :: GH_COARSE = 83491
  !> @}

  !> @defgroup fspace_basis Enumeration of function space basis/differential
  !!                        basis property descriptors (also "fspace_properties1").
  !> @{
  integer, public, parameter :: GH_BASIS      = 751
  integer, public, parameter :: GH_DIFF_BASIS = 767
  !> @}

  !> @defgroup gh_shape Enumeration of quadrature and/or evaluator property
  !!                    descriptors (if a kernel requires basis or
  !!                    differential-basis functions).
  !> @{
  ! Quadrature metadata
  integer, public, parameter :: GH_QUADRATURE_XYZ   = 912
  integer, public, parameter :: GH_QUADRATURE_XYoZ  = 849
  integer, public, parameter :: GH_QUADRATURE_XoYoZ = 701
  integer, public, parameter :: GH_QUADRATURE_face  = 539
  integer, public, parameter :: GH_QUADRATURE_edge  = 419
  ! Evaluator metadata
  integer, public, parameter :: GH_EVALUATOR        = 959
  !> @}

  !> @defgroup reference_element_data_items Enumeration of reference element
  !!                                        data items.
  !> @{
  integer, public, parameter :: normals_to_faces                    = 171
  integer, public, parameter :: normals_to_horizontal_faces         = 904
  integer, public, parameter :: normals_to_vertical_faces           = 333
  integer, public, parameter :: outward_normals_to_faces            = 007
  integer, public, parameter :: outward_normals_to_horizontal_faces = 618
  integer, public, parameter :: outward_normals_to_vertical_faces   = 802
  !> @}

  !> @defgroup mesh_data_items Enumeration of mesh data items.
  !> @{
  integer, public, parameter :: adjacent_face = 533
  !> @}

  !> @defgroup operates_on Enumeration of kernel iterator property descriptors.
  !> @{
  integer, public, parameter :: CELL_COLUMN = 396
  integer, public, parameter :: DOMAIN      = 945
  integer, public, parameter :: DOF         = 712
  !> @}

  !> Metadata for the argument type description, stored in the `arg_type` type
  !! as an array of `meta_args`. We need to know how many scalars, fields
  !! and/or operators are passed to the kernel and in what order they are
  !! passed. We also need to know how these scalars/fields/operators:
  !! - Are accessed (read, write, etc.) within the kernel;
  !! - What is the type of argument data;
  !! - What function space the fields and operators are on (w0, w1, etc.).
  !! In the case of operators there are two function spaces (to and from).
  !! Fields may have an optional metadata describing either a stencil access
  !! or, for inter-grid kernels, which mesh the field is on.
  type, public :: arg_type
     !> Type of a kernel argument (scalar, field, operator or a
     !! column-wise operator). One of {GH_SCALAR, GH_FIELD, GH_OPERATOR,
     !! GH_COLUMNWISE_OPERATOR}.
     integer :: argument_type
     !> Fortran primitive type of kernel argument data.
     !! One of {GH_REAL, GH_INTEGER}.
     integer :: data_type
     !> How the kernel argument data is accessed (e.g.\ read-only, update,
     !! global reduction). One of {GH_READ, GH_WRITE, GH_READWRITE,
     !! GH_INC, GH_SUM, GH_MIN, GH_MAX}.
     integer :: argument_access
     !> Function space "on" of a field argument or "to" of an operator argument.
     !! One of {W*, ANY_SPACE_[1-10]+, ANY_DISCONTINUOUS_SPACE_[1-10]+, ANY_W2}.
     integer :: fspace      = -1
     !> Function space "from" of an operator argument. One of {W*,
     !! ANY_SPACE_[1-10]+, ANY_DISCONTINUOUS_SPACE_[1-10]+, ANY_W2}.
     integer :: fspace_from = -1
     !> Optional metadata (fields only) for a type of stencil map to use.
     !! One of {XORY1D, X1D, Y1D, CROSS, REGION, CROSS2D}.
     integer :: stencil_map = -1
     !> Optional metadata (fields only) for inter-grid mapping kernels.
     !! One of {GH_FINE, GH_COARSE}.
     integer :: mesh_arg    = -1
  end type arg_type

  !> Optional metadata for the basis/differential basis functions required with
  !! the quadrature or evaluator data a particular function space, stored in
  !! the `func_type` type as an array of `meta_funcs`). This information is
  !! required when specifying `gh_shape` information for Gaussian quadrature
  !! type or evaluator target).
  type, public :: func_type
     !> Function space "on" of basis/differential basis functions. One of
     !! {W*, ANY_SPACE_[1-10]+, ANY_DISCONTINUOUS_SPACE_[1-10]+, ANY_W2}.
     integer :: fspace
     !> Basis/differential basis functions on a specified function space.
     !! One of {GH_BASIS, GH_DIFF_BASIS}.
     integer :: fspace_basis
     !> Optional metadata ({ "" }), must be a distinct property
     !! (e.g.\ differential basis functions if basis functions are already
     !! specified). One of {GH_BASIS, GH_DIFF_BASIS}.
     integer :: fspace_properties1 = -1
  end type func_type

  !> Optional metadata for the reference element data, stored in the
  !! `reference_element_data_type` type as an array of `meta_reference_element`.
  type, public :: reference_element_data_type
    !> One of {normals_to_faces, normals_to_horizontal_faces,
    !! normals_to_vertical_faces, outward_normals_to_faces,
    !! outward_normals_to_horizontal_faces, outward_normals_to_vertical_faces}.
    integer :: reference_element_data_item
  end type reference_element_data_type

  !> Optional metadata for the mesh data, stored in the `mesh_data_type` type as
  !! an array of `meta_mesh` (currently only supports `adjacent_face` array).
  type, public :: mesh_data_type
    integer :: mesh_data_item
  end type mesh_data_type

end module argument_mod



!-----------------------------------------------------------------------------
! Copyright (c) 2017-2020,  Met Office, on behalf of HMSO and Queen's Printer
! For further details please refer to the file LICENCE.original which you
! should have received as part of this distribution.
!-----------------------------------------------------------------------------
! LICENCE.original is available from the Met Office Science Repository Service:
! https://code.metoffice.gov.uk/trac/lfric/browser/LFRic/trunk/LICENCE.original
!-------------------------------------------------------------------------------

! Abstract base kernel type.
!-------------------------------------------------------------------------------
!> @brief Abstract base type for for kernels
module kernel_mod
implicit none
private

!-------------------------------------------------------------------------------
! Public types
!-------------------------------------------------------------------------------

type, public, abstract :: kernel_type
  private

end type

!-------------------------------------------------------------------------------
! Interfaces
!-------------------------------------------------------------------------------

end module kernel_mod



!-----------------------------------------------------------------------------
! Copyright (c) 2017-2020,  Met Office, on behalf of HMSO and Queen's Printer
! For further details please refer to the file LICENCE.original which you
! should have received as part of this distribution.
!-----------------------------------------------------------------------------
! LICENCE.original is available from the Met Office Science Repository Service:
! https://code.metoffice.gov.uk/trac/lfric/browser/LFRic/trunk/LICENCE.original
!-------------------------------------------------------------------------------

!> @brief A simple logging facility.
!>
!> If the code is being run serially, the logging information will be written
!> to the terminal. For parallel execution, the logging information will
!> be sent to files - one for each MPI task.
!>
!> @todo  At some point the serial version of Dynamo should also log to a file,
!>        but for now it is easier for developers if the code logs to stdout.


module log_mod

  use constants_mod, only : str_long, str_max_filename
  use, intrinsic :: iso_fortran_env, only : output_unit, error_unit

  implicit none

  private
  public initialise_logging, finalise_logging, &
         log_set_info_stream, log_set_alert_stream, &
         log_set_level, log_level, log_event

  !> Named logging level.
  !>
  !> Any integer can be used for the logging level but this name represents
  !> a break between level. Generally you will want to use these names.
  !>
  !> @{
  integer, public, parameter :: LOG_LEVEL_ALWAYS  = 100000
  integer, public, parameter :: LOG_LEVEL_ERROR   = 200
  integer, public, parameter :: LOG_LEVEL_WARNING = 150
  integer, public, parameter :: LOG_LEVEL_INFO    = 100
  integer, public, parameter :: LOG_LEVEL_DEBUG   =  50
  integer, public, parameter :: LOG_LEVEL_TRACE   =   0
  !> @}

  !> Space in which to marshal log messages.
  !>
  !> Although any string can be passed to log_event() this space is provided to
  !> prevent a proliferation of work spaces all over the code. It also means
  !> that should 160 characters be found to be insufficient it need only be
  !> changed in one place.
  !>
  character( str_long + str_max_filename ), public :: log_scratch_space

  integer, private, parameter :: EXIT_CODE_ON_ERROR = 1

  integer, private :: logging_level = LOG_LEVEL_INFO
  integer, private :: info_unit     = output_unit
  integer, private :: alert_unit    = error_unit

  integer, private :: log_unit_number = 10
  logical, private :: is_parallel = .false.
  character(len=:), allocatable :: petno

contains

  !> Set where information goes.
  !>
  !> If this routine is never called then information will default to standard
  !> out.
  !>
  !> @param unit The unit to send information to
  !>
  subroutine log_set_info_stream(unit)

    implicit none

    integer, intent( in ) :: unit

    info_unit = unit

  end subroutine log_set_info_stream

  !> Set where alerts go.
  !>
  !> If this routine is never called then alerts will default to standard
  !> error.
  !>
  !> @param unit The unit to send alerts to
  !>
  subroutine log_set_alert_stream(unit)

    implicit none

    integer, intent( in ) :: unit

    alert_unit = unit

  end subroutine log_set_alert_stream

  !> Set the level this logger responds to.
  !>
  !> Events ranked lower than the logging level will be accepted and dropped
  !> on the floor.
  !>
  !> @param level The new logging level to adopt.
  !>
  subroutine log_set_level(level)

    implicit none

    integer, intent( in ) :: level

    logging_level = level

  end subroutine log_set_level

  !> Gets the current logging level.
  !>
  !> Primarily used for testing purposes.
  !>
  !> @returns The logging level.
  !>
  function log_level()

    implicit none

    integer :: log_level

    log_level = logging_level

  end function


  !> Initialise logging functionality by opening the log files
  !> @param this_rank The number of the local rank
  !> @param total_ranks The total number pf ranks in the job
  !> @param app_name The name of the application. This will form part of the
  !>                 log file name(s)
  subroutine initialise_logging(this_rank, total_ranks, app_name)
    implicit none
    integer, intent(in) :: this_rank, total_ranks
    character(len=*), intent(in) :: app_name
    integer :: ios
    integer :: ilen
    character(len=:), allocatable :: logfilename
    character(len=12) :: fmt

    if (total_ranks > 1 ) then
      is_parallel = .true.
      ilen=int(log10(real(total_ranks-1)))+1
      write(fmt,'("(i",i0,".",i0,")")')ilen, ilen
      allocate(character(len=ilen) :: petno)
      write(petno,fmt)this_rank
      allocate(character(len=ilen+len_trim(app_name)+8) :: logfilename)
      write(logfilename,"(a,a,a,a,a)")"PET",petno,".",trim(app_name),".Log"
      open(unit=log_unit_number, file=logfilename, status='unknown', iostat=ios)
      if ( ios /= 0 )then
        write(error_unit,"('Cannot open logging file. iostat = ',i0)")ios
        stop EXIT_CODE_ON_ERROR
      end if
      call log_event('LFRic Logging System Version 1.0',LOG_LEVEL_ALWAYS)
    else
      is_parallel = .false.
    end if

  end subroutine initialise_logging

  !> Finalise logging functionality by closing the log files
  subroutine finalise_logging()
    implicit none
    integer :: ios
    if ( is_parallel ) then
      close(unit=log_unit_number,iostat=ios)
      if ( ios /= 0 )then
        write(error_unit,"('Cannot close logging file. iostat = ',i0)")ios
        stop EXIT_CODE_ON_ERROR
      end if
    end if
  end subroutine finalise_logging

  !> Log an event
  !>
  !> If the code is running on multiple MPI ranks, the event description will
  !> be sent to a log file. For serial executions, the event description is
  !> sent to the terminal along with timestamp and level information.
  !> For the most serious events (a severity level equal to
  !> or greater than LOG_LEVEL_ERROR), execution of the code will be aborted.
  !>
  !> @param message A description of the event.
  !> @param level   The severity of the event. Defaults to cInfoLevel.
  !>
  subroutine log_event(message, level)

    use, intrinsic :: iso_fortran_env, only : output_unit, error_unit

    implicit none

    character (*), intent( in ) :: message
    integer,       intent( in ) :: level

    integer        :: unit
    character (5)  :: tag
    character (8)  :: date_string
    character (10) :: time_string
    character (5)  :: zone_string

    logical :: abort_run = .false.

    if (level >= logging_level) then

      select case (level)
        case ( : LOG_LEVEL_DEBUG - 1)
          unit = info_unit
          tag  = 'TRACE'
        case (LOG_LEVEL_DEBUG : LOG_LEVEL_INFO - 1 )
          unit = info_unit
          tag  = 'DEBUG'
        case ( LOG_LEVEL_INFO : LOG_LEVEL_WARNING - 1 )
          unit = info_unit
          tag  = 'INFO '
        case ( LOG_LEVEL_WARNING : LOG_LEVEL_ERROR - 1)
          unit = alert_unit
          tag  = 'WARN '
        case ( LOG_LEVEL_ERROR : LOG_LEVEL_ALWAYS - 1)
          unit = alert_unit
          tag  = 'ERROR'
          abort_run = .true.
        case ( LOG_LEVEL_ALWAYS : )
          unit = info_unit
          tag  = 'INFO'
      end select

      call date_and_time( date=date_string, time=time_string, zone=zone_string)

      if(is_parallel)then
        unit = log_unit_number
        write (unit, '(A," ",A," ",A,"            PET",A," ",A)') &
                   date_string, time_string, tag, petno, trim( message )
      else
        write (unit, '(A,A,A,":",A,": ",A)') &
                   date_string, time_string, zone_string, tag, trim( message )
      end if

      ! If the severity level of the event is serious enough, stop the code.
      if ( abort_run ) then
        stop EXIT_CODE_ON_ERROR
      end if

    end if

  end subroutine log_event

end module log_mod



!-----------------------------------------------------------------------------
! Copyright (c) 2017-2020,  Met Office, on behalf of HMSO and Queen's Printer
! For further details please refer to the file LICENCE.original which you
! should have received as part of this distribution.
!-----------------------------------------------------------------------------
! LICENCE.original is available from the Met Office Science Repository Service:
! https://code.metoffice.gov.uk/trac/lfric/browser/LFRic/trunk/LICENCE.original
!-----------------------------------------------------------------------------
!
!> @brief Define enumerator variables that describe the different types of continuity.
!>
!> @details Enumerator variables that describe the different types of continuity
!>          that can be used to construct function spaces

module fs_continuity_mod

use constants_mod, only: i_native, str_short
use log_mod,       only: log_event, log_scratch_space, log_level_error

implicit none

private
public :: name_from_functionspace

character(*), private, parameter :: module_name = 'fs_continuity_mod'

!-------------------------------------------------------------------------------
! Module parameters
!-------------------------------------------------------------------------------
integer(i_native), public, parameter :: W0        = 173
integer(i_native), public, parameter :: W1        = 194
integer(i_native), public, parameter :: W2        = 889
integer(i_native), public, parameter :: W2V       = 857
integer(i_native), public, parameter :: W2H       = 884
integer(i_native), public, parameter :: W2broken  = 211
integer(i_native), public, parameter :: W2trace   = 213
integer(i_native), public, parameter :: W2Vtrace  = 666
integer(i_native), public, parameter :: W2Htrace  = 777
integer(i_native), public, parameter :: W3        = 424
integer(i_native), public, parameter :: Wtheta    = 274
integer(i_native), public, parameter :: Wchi      = 869

integer(i_native), public, parameter :: fs_enumerator(12) = [W0,       &
                                                             W1,       &
                                                             W2,       &
                                                             W2V,      &
                                                             W2H,      &
                                                             W2broken, &
                                                             W2trace,  &
                                                             W2Vtrace, &
                                                             W2Htrace, &
                                                             W3,       &
                                                             Wtheta,   &
                                                             Wchi]

character(str_short), public, parameter :: fs_name(12) &
         = [character(str_short)    :: 'W0',       &
                                       'W1',       &
                                       'W2',       &
                                       'W2V',      &
                                       'W2H',      &
                                       'W2broken', &
                                       'W2trace',  &
                                       'W2Htrace', &
                                       'W2Vtrace', &
                                       'W3',       &
                                       'Wtheta',   &
                                       'Wchi']

contains

  !> Gets the name corresponding to a particular function space identifier.
  !>
  !> @param[in] fs One of the function space enumerations.
  !>
  !> @return String holding the function space name.
  !>
  function name_from_functionspace( fs )

    implicit none

    integer(i_native), intent(in) :: fs

    character(str_short) :: name_from_functionspace

    integer(i_native) :: fs_index

    fs_index = 1
    do
      if (fs_enumerator(fs_index) == fs) then
        name_from_functionspace = fs_name(fs_index)
        return
      end if
      fs_index = fs_index + 1
      if (fs_index > ubound(fs_enumerator,1)) then
        write( log_scratch_space, &
               '(A, ": Unrecognised function space: ",I0)' ) module_name, fs
        call log_event( log_scratch_space, log_level_error )
      end if
    end do

  end function name_from_functionspace

end module fs_continuity_mod

! BSD 3-Clause License
!
! Copyright (c) 2017-2022, Science and Technology Facilities Council
! All rights reserved.
!
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
!
! * Redistributions of source code must retain the above copyright notice, this
!   list of conditions and the following disclaimer.
!
! * Redistributions in binary form must reproduce the above copyright notice,
!   this list of conditions and the following disclaimer in the documentation
!   and/or other materials provided with the distribution.
!
! * Neither the name of the copyright holder nor the names of its
!   contributors may be used to endorse or promote products derived from
!   this software without specific prior written permission.
!
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
! AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
! IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
! FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
! DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
! SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
! CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
! OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
! OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! -----------------------------------------------------------------------------
! Author R. W. Ford, STFC Daresbury Lab
! Modified by J. Henrichs, Bureau of Meteorology
! Modified by I. Kavcic, Met Office

module testkern_w0_kernel_mod

  use argument_mod
  use kernel_mod
  use fs_continuity_mod, only: W0

  use constants_mod

  implicit none

  private

  type, public, extends(kernel_type) :: testkern_w0_kernel_type
     private
     type(arg_type), dimension(4) :: meta_args =       &
          (/ arg_type(gh_field, gh_real, gh_inc,  w0), &
             arg_type(gh_field, gh_real, gh_read, w0), &
             arg_type(gh_field*3, gh_real, gh_read, w0), &
             arg_type(gh_scalar, gh_logical, gh_read)  &
           /)
     integer :: operates_on = cell_column
   contains
     procedure, nopass :: code => testkern_w0_code
  end type testkern_w0_kernel_type

  public :: testkern_w0_code

contains

  subroutine testkern_w0_code(nlayers, fld1, fld2, chi1, chi2, chi3, &
                              some_logical, ndf_w0, undf_w0, map_w0)

    implicit none

    integer(kind=i_def), intent(in)                     :: nlayers
    integer(kind=i_def)                                 :: ndf_w0, undf_w0
    real(kind=r_def), dimension(undf_w0), intent(inout) :: fld1
    real(kind=r_def), dimension(undf_w0), intent(in)    :: fld2
    real(kind=r_def), dimension(undf_w0), intent(in)    :: chi1,chi2,chi3
    logical(kind=l_def), intent(in)                     :: some_logical
    integer(kind=i_def), dimension(ndf_w0)              :: map_w0

    integer(kind=i_def)                                 :: i, k

    do k=0, nlayers-1
      do i=1, ndf_w0
        fld1(map_w0(i)+k) = fld1(map_w0(i)+k) + fld2(map_w0(i)+k)
        if (some_logical) then
          fld1(map_w0(i)+k) = fld1(map_w0(i)+k) + 1
        endif
      end do
    end do

  end subroutine testkern_w0_code

end module testkern_w0_kernel_mod

program main_update
  use read_kernel_data_mod, only : ReadKernelDataType
  use testkern_w0_kernel_mod, only : testkern_w0_code
  use constants_mod, only : i_def, l_def, r_bl, r_def, r_double, r_ncdf, r_phys, r_second, r_single, r_solver, r_tran, r_um
  integer(kind=i_def) :: loop0_start
  integer(kind=i_def) :: loop0_stop
  integer(kind=i_def) :: nlayers
  real(kind=r_def), allocatable, dimension(:) :: field1_data
  real(kind=r_def), allocatable, dimension(:) :: field2_data
  real(kind=r_def), allocatable, dimension(:) :: chi_1_data
  real(kind=r_def), allocatable, dimension(:) :: chi_2_data
  real(kind=r_def), allocatable, dimension(:) :: chi_3_data
  logical(kind=l_def) :: some_logical
  integer(kind=i_def) :: ndf_w0
  integer(kind=i_def) :: undf_w0
  integer(kind=i_def), allocatable, dimension(:,:) :: map_w0
  integer(kind=i_def) :: cell
  type(ReadKernelDataType) :: extract_psy_data
  integer(kind=i_def) :: cell_post
  real(kind=r_def), allocatable, dimension(:) :: field1_data_post

  call extract_psy_data%OpenRead('main', 'update')
  call extract_psy_data%ReadVariable('chi_1_data', chi_1_data)
  call extract_psy_data%ReadVariable('chi_2_data', chi_2_data)
  call extract_psy_data%ReadVariable('chi_3_data', chi_3_data)
  call extract_psy_data%ReadVariable('field1_data', field1_data)
  call extract_psy_data%ReadVariable('field2_data', field2_data)
  call extract_psy_data%ReadVariable('loop0_start', loop0_start)
  call extract_psy_data%ReadVariable('loop0_stop', loop0_stop)
  call extract_psy_data%ReadVariable('map_w0', map_w0)
  call extract_psy_data%ReadVariable('ndf_w0', ndf_w0)
  call extract_psy_data%ReadVariable('nlayers', nlayers)
  call extract_psy_data%ReadVariable('some_logical', some_logical)
  call extract_psy_data%ReadVariable('undf_w0', undf_w0)
  call extract_psy_data%ReadVariable('cell_post', cell_post)
  cell = 0
  call extract_psy_data%ReadVariable('field1_data_post', field1_data_post)
  do cell = loop0_start, loop0_stop, 1
    call testkern_w0_code(nlayers, field1_data, field2_data, chi_1_data, chi_2_data, chi_3_data, some_logical, ndf_w0, undf_w0, &
&map_w0(:,cell))
  enddo
  if (cell == cell_post) then
    PRINT *, "cell correct"
  else
    PRINT *, "cell incorrect. Values are:"
    PRINT *, cell
    PRINT *, "cell values should be:"
    PRINT *, cell_post
  end if
  if (ALL(field1_data - field1_data_post == 0.0)) then
    PRINT *, "field1_data correct"
  else
    PRINT *, "field1_data incorrect. Values are:"
    PRINT *, field1_data
    PRINT *, "field1_data values should be:"
    PRINT *, field1_data_post
  end if

end program main_update
