cmake_minimum_required(VERSION 3.5)
project(cuckoo_filter)

set(CMAKE_CXX_STANDARD 11)

# Use the conda Python environment - set these BEFORE find_package
set(Python3_EXECUTABLE "/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3")
set(Python3_ROOT_DIR "/Users/zongyikun/opt/anaconda3/envs/python310_arm")
set(PYTHON_EXECUTABLE "${Python3_EXECUTABLE}")

# Find Python
find_package(Python3 3.10 COMPONENTS Interpreter Development REQUIRED)

# Find pybind11
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import pybind11; import os; print(os.path.dirname(pybind11.__file__))"
    OUTPUT_VARIABLE PYTHON_PYBIND11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
)
if(PYTHON_PYBIND11_DIR)
    set(pybind11_DIR "${PYTHON_PYBIND11_DIR}/share/cmake/pybind11")
endif()
find_package(pybind11 REQUIRED)

include_directories(${CMAKE_SOURCE_DIR}/src ${Python3_INCLUDE_DIRS})

# Find OpenSSL (try homebrew path first)
set(OPENSSL_ROOT_DIR "/opt/homebrew/opt/openssl@3")
find_package(OpenSSL REQUIRED)
include_directories(${OPENSSL_INCLUDE_DIR} /opt/homebrew/opt/openssl@3/include)

pybind11_add_module(cuckoo_filter_module
    cuckoo_bind.cpp
)

target_link_libraries(cuckoo_filter_module PRIVATE 
    ${OPENSSL_CRYPTO_LIBRARY} 
    ${OPENSSL_SSL_LIBRARY}
)
