cmake_minimum_required(VERSION 3.15)
project(FileProcessorServer CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Usa o pkg-config do Ubuntu para localizar o gRPC e Protobuf
find_package(PkgConfig REQUIRED)
pkg_check_modules(GRPC REQUIRED grpc++)
pkg_check_modules(PROTOBUF REQUIRED protobuf)

set(PROTO_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../proto")
set(PROTO_FILE "${PROTO_DIR}/file_processor.proto")

set(PROTO_SRC "${CMAKE_CURRENT_BINARY_DIR}/file_processor.pb.cc")
set(PROTO_HDR "${CMAKE_CURRENT_BINARY_DIR}/file_processor.pb.h")
set(GRPC_SRC "${CMAKE_CURRENT_BINARY_DIR}/file_processor.grpc.pb.cc")
set(GRPC_HDR "${CMAKE_CURRENT_BINARY_DIR}/file_processor.grpc.pb.h")

# No Ubuntu, o apt-get instala o compilador e o plugin nestes caminhos fixos
set(PROTOC_COMPILER "/usr/bin/protoc")
set(GRPC_CPP_PLUGIN "/usr/bin/grpc_cpp_plugin")

add_custom_command(
    OUTPUT ${PROTO_SRC} ${PROTO_HDR} ${GRPC_SRC} ${GRPC_HDR}
    COMMAND ${PROTOC_COMPILER}
    ARGS --grpc_out="${CMAKE_CURRENT_BINARY_DIR}"
         --cpp_out="${CMAKE_CURRENT_BINARY_DIR}"
         -I "${PROTO_DIR}"
         --plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN}
         "${PROTO_FILE}"
    DEPENDS "${PROTO_FILE}"
)

include_directories("${CMAKE_CURRENT_BINARY_DIR}")

add_executable(server
    server.cc
    ${PROTO_SRC}
    ${GRPC_SRC}
)

# Link direto com as bibliotecas do sistema (gpr corrige o erro 'gpr_log')
target_link_libraries(server
    grpc++ grpc gpr absl_synchronization
    protobuf
)
target_link_options(server PRIVATE -Wl,--copy-dt-needed-entries)
