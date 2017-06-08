#!/bin/python3

import os
import sys
import argparse

class BasicCMakeGenerator:

    CMakeFileName = "CMakeLists.txt"

    def __init__(self, args, paths):
        self.paths = paths
        self.minCMakeVersion = args.minCMakeVersion
        self.projectName = args.projectName
        self.cxxVersion = args.cppVersion
        self.defaultTargetType = args.defaultTargetType

    def generateCMakeFileContent(self):
        from io import StringIO
        strIO = StringIO()

        strIO.write("set(PROJECT_" + self.projectName.upper() + " \"" + self.projectName + "\")\n")
        strIO.write("project(${PROJECT_" + self.projectName.upper() + "} CXX)\n")
        strIO.write("\n")
        strIO.write("set(CMAKE_CXX_STANDARD " + self.cxxVersion + ")\n")
        strIO.write("\n")
        strIO.write("#add_definitions(\"-DDEVELOPMENT_BUILD\")\n")
        strIO.write("set(" + self.projectName.upper() + "_PUBLIC_HEADERS \"" + os.path.join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubHeaders"][len(self.projectName) + 1:]) + "\")\n")
        strIO.write("set(" + self.projectName.upper() + "_PRIVATE_HEADERS \"" + os.path.join("${CMAKE_CURRENT_LIST_DIR}", self.paths["privHeaders"][len(self.projectName) + 1:]) + "\")\n")
        strIO.write("set(" + self.projectName.upper() + "_SRC \"" + os.path.join("${CMAKE_CURRENT_LIST_DIR}", self.paths["src"][len(self.projectName) + 1:]) + "\")\n")
        strIO.write("\n")

        if self.defaultTargetType == "lib":
            strIO.write("add_library(${PROJECT_" + self.projectName.upper() + "} "
                                                 + " ${" + self.projectName.upper() + "_SRC}" \
                                                 + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                                                 + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                                                 + ")\n")
        else:
            strIO.write("add_executable(${PROJECT_" + self.projectName.upper() + "} "
                                                 + " ${" + self.projectName.upper() + "_SRC}" \
                                                 + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                                                 + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                                                 + ")\n")

        strIO.write("target_include_directories(${PROJECT_" + self.projectName.upper() + "} PUBLIC \"" + \
                    os.path.join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubHeaders"][len(self.projectName) + 1:]) + "\")")

        strIO.write("\n")

        return strIO.getvalue()


class MainCMakeGenerator(BasicCMakeGenerator):

    def __init__(self, args, paths):
        super(MainCMakeGenerator, self).__init__(args, paths)

    def generateCMakeFileContent(self):
        from io import StringIO
        strIO = StringIO()

        strIO.write("cmake_minimum_required(VERSION " + self.minCMakeVersion  + ")\n")
        strIO.write(super(MainCMakeGenerator, self).generateCMakeFileContent())

        return strIO.getvalue()


def generatePaths(args):
    base = args.projectName

    docs = os.path.join(base, "documentation")

    code = os.path.join(base, "code")
    pub = os.path.join(code, "public")
    priv = os.path.join(code, "private")
    pubInc = os.path.join(pub, "include")
    privInc = os.path.join(priv, "include")
    pubHeaders = os.path.join(pubInc, base)
    privHeaders = os.path.join(privInc, base)
    src = os.path.join(code, "src")

    paths = { "base": base, "docs": docs, "code" : code, "pub" : pub, "priv" : priv,\
              "pubHeaders" : pubHeaders, "privHeaders" : privHeaders, "src" : src, \
               "pubInc" : pubInc, "privInc" : privInc}

    for name, d in paths.items():
        os.makedirs(d, 0o755, True)

    return paths


def generateCMakeFiles(paths, args):
    cmakeGenerator = MainCMakeGenerator(args, paths)

    f = open(os.path.join(paths["base"], MainCMakeGenerator.CMakeFileName), "w")
    f.write(cmakeGenerator.generateCMakeFileContent())
    f.close()


if __name__ == "__main__":
    print("Generating your project!\n")

    argParser = argparse.ArgumentParser(description="Generates the base structure of a new c++ project.")
    argParser.add_argument("projectName", help="The name of your new project.")
    argParser.add_argument("--cppVersion", help="The c++ standard that the project should use. Default is 14.", choices=["03","11","14","17"], default="14")
    argParser.add_argument("--minCMakeVersion", default="3.8.1", help="CMake version requirement.")
    argParser.add_argument("--defaultTargetType", choices=["lib", "exec"], default="lib", help="The type of target that will be built in the project(library, executable). Default value is library.")
    args = argParser.parse_args()

    paths = generatePaths(args)
    generateCMakeFiles(paths, args)

