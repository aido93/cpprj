cmake_minimum_required(VERSION 3.0.2)
project($prj_name)

set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} $cxx_flags")
set( CMAKE_EXE_LINKER_FLAGS "$linker_flags")
set( CMAKE_CXX_COMPILER $cxx)
set( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_COVERAGE_COMPILE_FLAGS}" )
include_directories( $inc_dirs ./include/ )

set(SOURCE_FILES
		src/main.cpp
	)

add_executable($prj_name ${SOURCE_FILES})
target_link_libraries($prj_name)
