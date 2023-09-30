program main_update
  use read_kernel_data_mod, only : ReadKernelDataType
  use testkern_w0_kernel_mod, only : testkern_w0_code
  use ,intrinsic::iso_fortran_env, only : int32, real32, real64
  integer, parameter :: r_def = real64
  integer, parameter :: r_second = real64
  integer, parameter :: r_solver = real32
  integer, parameter :: r_tran = real32
  integer, parameter :: i_def = int32
  integer, parameter :: l_def = int32
  integer(kind=i_def) :: loop0_start
  integer(kind=i_def) :: loop0_stop
  integer(kind=i_def) :: nlayers
  logical(kind=l_def) :: some_logical
  integer(kind=i_def) :: ndf_w0
  integer(kind=i_def) :: undf_w0
  integer(kind=i_def), allocatable, dimension(:,:) :: map_w0
  integer(kind=i_def) :: cell
  real(kind=r_def), allocatable, dimension(:) :: field1
  real(kind=r_def), allocatable, dimension(:) :: field2
  real(kind=r_def), allocatable, dimension(:) :: chi_1
  real(kind=r_def), allocatable, dimension(:) :: chi_2
  real(kind=r_def), allocatable, dimension(:) :: chi_3
  type(ReadKernelDataType) :: extract_psy_data
  integer(kind=i_def) :: cell_post
  real(kind=r_def), allocatable, dimension(:) :: field1_post

  call extract_psy_data%OpenRead('main', 'update')
  call extract_psy_data%ReadVariable('chi%1', chi_1)
  call extract_psy_data%ReadVariable('chi%2', chi_2)
  call extract_psy_data%ReadVariable('chi%3', chi_3)
  call extract_psy_data%ReadVariable('field1', field1)
  call extract_psy_data%ReadVariable('field2', field2)
  call extract_psy_data%ReadVariable('loop0_start', loop0_start)
  call extract_psy_data%ReadVariable('loop0_stop', loop0_stop)
  call extract_psy_data%ReadVariable('map_w0', map_w0)
  call extract_psy_data%ReadVariable('ndf_w0', ndf_w0)
  call extract_psy_data%ReadVariable('nlayers', nlayers)
  call extract_psy_data%ReadVariable('some_logical', some_logical)
  call extract_psy_data%ReadVariable('undf_w0', undf_w0)
  call extract_psy_data%ReadVariable('cell_post', cell_post)
  cell = 0
  call extract_psy_data%ReadVariable('field1_post', field1_post)
  do cell = loop0_start, loop0_stop, 1
    call testkern_w0_code(nlayers, field1, field2, chi_1, chi_2, chi_3, some_logical, ndf_w0, undf_w0, map_w0(:,cell))
  enddo
  if (cell == cell_post) then
    PRINT *, "cell correct"
  else
    PRINT *, "cell incorrect. Values are:"
    PRINT *, cell
    PRINT *, "cell values should be:"
    PRINT *, cell_post
  end if
  if (ALL(field1 - field1_post == 0.0)) then
    PRINT *, "field1 correct"
  else
    PRINT *, "field1 incorrect. Values are:"
    PRINT *, field1
    PRINT *, "field1 values should be:"
    PRINT *, field1_post
  end if

end program main_update
