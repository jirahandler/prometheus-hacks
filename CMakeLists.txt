cmake_minimum_required(VERSION 3.3.2 FATAL_ERROR)
cmake_policy(VERSION 3.3.2)


#TODO
# + add support for Apple systems (needs an apple part??)
# + make sure it correctly builds on the cobalt testbed
# + verify python build.

## project(lepton_injector VERSION 1.0.0 DESCRIPTION "lepton injector library")
project(lepton_injector VERSION 1.0.0 LANGUAGES CXX C)

include(GNUInstallDirs)

SET(CMAKE_CXX_STANDARD 11)
SET(CMAKE_C_STANDARD 99)
## enable_language(cxx)
SET (CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake
                     ${CMAKE_SOURCE_DIR}/cmake/Packages)

INCLUDE (SuiteSparse)
INCLUDE (Python)

set(CMAKE_CXX_FLAGS_DEBUG  "-g -O0")

if(CMAKE_VERSION VERSION_LESS 3.12.0)
    if(Python_ROOT_DIR)
        MESSAGE(WARNING "Python_ROOT_DIR is set but will be ignored by this version of CMake; set PYTHON_EXECUTABLE instead")
    endif()
    find_package(PythonInterp)
    find_package(PythonLibs)
    set(PYTHON_FOUND PYTHONLIBS_FOUND AND PYTHONINTERP_FOUND)
    set(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR}) # Compatibility for older CMake
else()
    if(PYTHON_EXECUTABLE)
        MESSAGE(WARNING "PYTHON_EXECUTABLE is set but will be ignored by this version of CMake; set Python_ROOT_DIR instead")
    endif()
    find_package(Python COMPONENTS Interpreter Development)
    set(PYTHON_FOUND Python_Interpreter_FOUND AND Python_Development_FOUND)
    set(PYTHON_EXECUTABLE "${Python_EXECUTABLE}")
    set(PYTHON_INCLUDE_DIRS "${Python_INCLUDE_DIRS}")
    set(PYTHON_LIBRARIES "${Python_LIBRARIES}")
    set(PYTHON_VERSION_MAJOR "${Python_VERSION_MAJOR}")
    set(PYTHON_VERSION_MINOR "${Python_VERSION_MINOR}")
endif()
if(PYTHON_FOUND)
    MESSAGE("-- Found python at ${PYTHON_INCLUDE_DIRS}")
    MESSAGE("-- Will build python!")
else()
    MESSAGE(WARNING "!! Python Not Found !!")
    MESSAGE("!! Skipping Python Module !!")
endif()
if(DEFINED ENV{SROOT})
    set(HDF5_ROOT ${SROOT})
endif()
find_package(HDF5 REQUIRED)
if(HDF5_FOUND)
    MESSAGE("-- Found hdf5 at ${HDF5_INCLUDE_DIR}")
    include_directories(${HDF5_INCLUDE_DIR})
    set(_hdf5_libs hdf5 hdf5_cpp)
endif()

# find boost
find_package(Boost REQUIRED)
if(Boost_FOUND)
    MESSAGE("-- Found Boost at ${Boost_INCLUDE_DIRS}")
    include_directories(${Boost_INCLUDE_DIRS})
else()
    MESSAGE(FATAL_ERROR "Unable to find boost")
endif()

find_package(photospline REQUIRED)

if(photospline_FOUND)
    MESSAGE("-- photospline found")
endif()

# Add public headers to the include path for all targets
include_directories(${CMAKE_SOURCE_DIR}/public)

#core files 
LIST (APPEND core_SOURCES
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/BasicInjectionConfiguration.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/LeptonInjector.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/Controller.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/Coordinates.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/DataWriter.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/EventProps.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/Particle.cxx
    ${CMAKE_SOURCE_DIR}/private/LeptonInjector/Random.cxx
    ${CMAKE_SOURCE_DIR}/private/earthmodel-service/EarthModelCalculator.cxx
    ${CMAKE_SOURCE_DIR}/private/earthmodel-service/EarthModelService.cxx
    ${CMAKE_SOURCE_DIR}/private/phys-services/LICrossSection.cxx
)

# Create the main libLeptonInjector.so shared library
add_library( lepton_injector SHARED ${core_SOURCES} )

set_target_properties(lepton_injector PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    OUTPUT_NAME LeptonInjector)

MESSAGE("")
MESSAGE("Linking ...")
MESSAGE("    hdf5 ${HDF5_LIBRARIES}")
MESSAGE("    boost ${Boost_LIBRARIES}")
target_link_libraries(lepton_injector PUBLIC ${HDF5_LIBRARIES} ${Boost_LIBRARIES} photospline)
MESSAGE("")

install(TARGETS lepton_injector
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(DIRECTORY "${CMAKE_SOURCE_DIR}/public/"
    DESTINATION "include"
    FILES_MATCHING PATTERN "*.h")

# write and install pkg-config file
file(WRITE "LeptonInjector.pc" "prefix=${CMAKE_INSTALL_PREFIX}\n")
file(APPEND "LeptonInjector.pc" "libdir=${CMAKE_INSTALL_PREFIX}/lib\n")
file(APPEND "LeptonInjector.pc" "includedir=${CMAKE_INSTALL_PREFIX}/include\n")
file(APPEND "LeptonInjector.pc" "Name: LeptonInjector\n")
file(APPEND "LeptonInjector.pc" "Description: Generates neutrino events for large volume cherenkov telescopes\n")
file(APPEND "LeptonInjector.pc" "URL: https://github.com/IceCubeOpenSource/LeptonInjector\n")
file(APPEND "LeptonInjector.pc" "Version: 1.0.0\n")
file(APPEND "LeptonInjector.pc" "Requires: photospline\n")
file(APPEND "LeptonInjector.pc" "Libs: -L${CMAKE_INSTALL_PREFIX}/lib\n")
file(APPEND "LeptonInjector.pc" "Cflags: -I${CMAKE_INSTALL_PREFIX}/include\n")
  
install(FILES "LeptonInjector.pc" DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig")

# build and install pyhton module
if(DEFINED ENV{SROOT})
    set(Python_ROOT_DIR ${SROOT})
endif()
find_package(PythonInterp)
find_package(PythonLibs)
set(PYTHON_FOUND PYTHONLIBS_FOUND AND PYTHONINTERP_FOUND)
find_package(Boost REQUIRED COMPONENTS python)
if(PYTHON_FOUND)
    MESSAGE("-- Found python at ${PYTHON_INCLUDE_DIR}")
    MESSAGE("-- Will build python!")
else()
    MESSAGE("!! Python Not Found !!")
    MESSAGE("!! Skipping Python Module !!")
endif()



IF(PYTHON_FOUND)
    # Find the correct version of Boost.Python
    if(${PYTHON_VERSION_MAJOR} EQUAL 3)
        MESSAGE("-- Searching for python3 compatible boost_python")
        find_package(Boost COMPONENTS python3 QUIET)
        if(NOT Boost_FOUND)
            # Maybe it isn't labeled as python3? Search without a version and hope for the best
            find_package(Boost COMPONENTS python QUIET)
        endif()
    else()
        MESSAGE("-- Searching for python2 compatible boost_python")
        find_package(Boost COMPONENTS python QUIET)
    endif()

    include_directories(${Boost_INCLUDE_DIRS})
    
    # --- Build LeptonInjector Python module ---
    add_library( LeptonInjectorModule SHARED 
        ${CMAKE_SOURCE_DIR}/private/pybindings/LeptonInjector.cxx
    )
    set_target_properties( LeptonInjectorModule PROPERTIES 
        LINKER_LANGUAGE CXX 
        OUTPUT_NAME "LeptonInjector" 
        PREFIX "" 
        SUFFIX ".so"
    )
    # Add Python include directories to the target to find pyconfig.h
    target_include_directories(LeptonInjectorModule PRIVATE ${PYTHON_INCLUDE_DIRS})
    # Link against the main lepton_injector library
    target_link_libraries(LeptonInjectorModule PRIVATE lepton_injector ${Boost_LIBRARIES} ${Python_LIBRARIES})
    
    # --- Build EarthModelService Python module ---
    add_library( EarthModelServiceModule SHARED 
        ${CMAKE_SOURCE_DIR}/private/pybindings/earthmodel-service.cxx
    )
    set_target_properties( EarthModelServiceModule PROPERTIES 
        LINKER_LANGUAGE CXX 
        OUTPUT_NAME "EarthModelService" 
        PREFIX "" 
        SUFFIX ".so"
    )
    # Add Python include directories to the target to find pyconfig.h
    target_include_directories(EarthModelServiceModule PRIVATE ${PYTHON_INCLUDE_DIRS})
    # Link against the main lepton_injector library
    target_link_libraries(EarthModelServiceModule PRIVATE lepton_injector ${Boost_LIBRARIES} ${Python_LIBRARIES})
    
    # Set the runtime path so the python modules can find libLeptonInjector.so
    set_target_properties(LeptonInjectorModule EarthModelServiceModule PROPERTIES
        INSTALL_RPATH "$ORIGIN/../../"
    )

    # --- Find python install location and install both modules ---
    EXECUTE_PROCESS( COMMAND ${PYTHON_EXECUTABLE} -c
        "from distutils.sysconfig import get_python_lib; print(get_python_lib(prefix=''))"
        OUTPUT_VARIABLE PYTHON_MODULE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE)
        
    if(PYTHON_MODULE_DIR)
        INSTALL(TARGETS LeptonInjectorModule EarthModelServiceModule LIBRARY DESTINATION ${PYTHON_MODULE_DIR})
    elseif(Python_SITELIB)
        INSTALL(TARGETS LeptonInjectorModule EarthModelServiceModule LIBRARY DESTINATION ${Python_SITELIB})
    endif()
ELSE(NOT PYTHON FOUND)
    MESSAGE("-- no python. skipping")
ENDIF(PYTHON_FOUND)


MESSAGE("")
MESSAGE("Done!")
MESSAGE("Run `make` then `make install`")

