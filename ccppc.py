import argparse
import re
import sys
from enum import Enum
import subprocess
import os

# Author: Alexandros Bouzalas

class Compiler(Enum):
    CLANG = "clang++"
    GCC = "g++"

DEFAULT_COMPILER = Compiler.CLANG
DEFAULT_CPP_VERSION = 17

def build_compile_command(dependencies, filename):
    return f"{DEFAULT_COMPILER.value} {filename} {' '.join(dependencies)} -std=c++{DEFAULT_CPP_VERSION}"

def compile(compile_command):
    print("\n\033[1;33mRunning:\033[0m\n")
    print(f"\033[1;32m{compile_command}\033[0m\n")
    subprocess.run(compile_command.split(" "))
    print("\033[1;33mOutput:\033[0m\n")

def read_file_parameter(filename):
    dependencies = collect_dependencies_recursive(filename, set())
    compile_command = build_compile_command(list(dependencies), filename)
    compile(compile_command)

def collect_dependencies_recursive(filename, visited_files):
    dependencies = set()
    base_path = os.path.dirname(filename)

    if filename in visited_files:
        return dependencies  # Avoid infinite loops by returning if file was already visited

    visited_files.add(filename)

    try:
        with open(filename, 'r') as source_code:
            for line in source_code.readlines():
                if "#include" in line:
                    line = line.split('"')
                    if len(line) == 3:
                        include_file = line[1].replace('.hpp', '.cpp')
                        if not include_file.startswith("/"):  # Assuming non-absolute paths need base_path
                            include_file = os.path.join(base_path, include_file)
                        dependencies.add(include_file)

                        # Recursively collect dependencies of the dependency
                        dependencies.update(collect_dependencies_recursive(include_file.replace('.cpp', '.hpp'), visited_files))
    except FileNotFoundError:
        print(f"Warning: Dependency file {filename} not found. Skipping.")

    return dependencies

def terminate_with_help(parser):
    parser.print_help()
    sys.exit(1)

def valid_file(filename):
    if not re.match(r".+\.(cpp|cxx|cc|C)$", filename):
        raise argparse.ArgumentTypeError("Invalid source file extension. Must be .cpp, .cxx, .cc, or .C")
    return filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="C/CPP compilation helper with user-defined flags and automatic dependency detection/inclusion")
    parser.add_argument("filename", type=valid_file, help="Source code file to compile")
    parser.add_argument("--compiler", type=Compiler, choices=list(Compiler), help="Compiler (g++, clang++)",
                        default=Compiler.CLANG)
    parser.add_argument("--version", choices=['98', '11', '14', '17', '20'], help="C++ version (98, 11, 14, 17, 20)",
                        default='17')
    args = parser.parse_args()

    DEFAULT_CPP_VERSION = args.version
    DEFAULT_COMPILER = args.compiler

    read_file_parameter(args.filename)
