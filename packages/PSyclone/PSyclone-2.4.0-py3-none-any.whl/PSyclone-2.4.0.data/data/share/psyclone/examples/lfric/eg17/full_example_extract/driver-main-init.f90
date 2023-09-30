program main_init
  use read_kernel_data_mod, only : ReadKernelDataType
  use ,intrinsic::iso_fortran_env, only : int32, real32, real64
  integer, parameter :: r_def = real64
  integer, parameter :: r_second = real64
  integer, parameter :: r_solver = real32
  integer, parameter :: r_tran = real32
  integer, parameter :: i_def = int32
  integer, parameter :: l_def = int32
  integer(kind=i_def) :: loop0_start
  integer(kind=i_def) :: loop0_stop
  integer(kind=i_def) :: df
  integer(kind=i_def) :: loop1_start
  integer(kind=i_def) :: loop1_stop
  real(kind=r_def) :: one
  real(kind=r_def), allocatable, dimension(:) :: field1
  real(kind=r_def), allocatable, dimension(:) :: field2
  type(ReadKernelDataType) :: extract_psy_data
  integer(kind=i_def) :: df_post
  real(kind=r_def), allocatable, dimension(:) :: field1_post
  real(kind=r_def), allocatable, dimension(:) :: field2_post

  call extract_psy_data%OpenRead('main', 'init')
  call extract_psy_data%ReadVariable('loop0_start', loop0_start)
  call extract_psy_data%ReadVariable('loop0_stop', loop0_stop)
  call extract_psy_data%ReadVariable('loop1_start', loop1_start)
  call extract_psy_data%ReadVariable('loop1_stop', loop1_stop)
  call extract_psy_data%ReadVariable('one', one)
  call extract_psy_data%ReadVariable('df_post', df_post)
  df = 0
  call extract_psy_data%ReadVariable('field1_post', field1_post)
  ALLOCATE(field1, mold=field1_post)
  field1 = 0
  call extract_psy_data%ReadVariable('field2_post', field2_post)
  ALLOCATE(field2, mold=field2_post)
  field2 = 0
  do df = loop0_start, loop0_stop, 1
    field1(df) = 0.0_r_def
  enddo
  do df = loop1_start, loop1_stop, 1
    field2(df) = one
  enddo
  if (df == df_post) then
    PRINT *, "df correct"
  else
    PRINT *, "df incorrect. Values are:"
    PRINT *, df
    PRINT *, "df values should be:"
    PRINT *, df_post
  end if
  if (ALL(field1 - field1_post == 0.0)) then
    PRINT *, "field1 correct"
  else
    PRINT *, "field1 incorrect. Values are:"
    PRINT *, field1
    PRINT *, "field1 values should be:"
    PRINT *, field1_post
  end if
  if (ALL(field2 - field2_post == 0.0)) then
    PRINT *, "field2 correct"
  else
    PRINT *, "field2 incorrect. Values are:"
    PRINT *, field2
    PRINT *, "field2 values should be:"
    PRINT *, field2_post
  end if

end program main_init
