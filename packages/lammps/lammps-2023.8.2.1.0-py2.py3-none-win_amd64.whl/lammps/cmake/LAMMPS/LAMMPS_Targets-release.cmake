#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "LAMMPS::lmp" for configuration "Release"
set_property(TARGET LAMMPS::lmp APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(LAMMPS::lmp PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/./lmp.exe"
  )

list(APPEND _cmake_import_check_targets LAMMPS::lmp )
list(APPEND _cmake_import_check_files_for_LAMMPS::lmp "${_IMPORT_PREFIX}/./lmp.exe" )

# Import target "LAMMPS::lammps" for configuration "Release"
set_property(TARGET LAMMPS::lammps APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(LAMMPS::lammps PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/./lammps.lib"
  )

list(APPEND _cmake_import_check_targets LAMMPS::lammps )
list(APPEND _cmake_import_check_files_for_LAMMPS::lammps "${_IMPORT_PREFIX}/./lammps.lib" )

# Import target "LAMMPS::phana" for configuration "Release"
set_property(TARGET LAMMPS::phana APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(LAMMPS::phana PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/./phana.exe"
  )

list(APPEND _cmake_import_check_targets LAMMPS::phana )
list(APPEND _cmake_import_check_files_for_LAMMPS::phana "${_IMPORT_PREFIX}/./phana.exe" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
