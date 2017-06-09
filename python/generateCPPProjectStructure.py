#!/bin/python3

import os
import sys
import argparse
from os.path import join
from io import StringIO

class BasicCMakeGenerator:
    CMakeFileName = "CMakeLists.txt"

    def __init__(self, args, paths):
        self.paths = paths
        self.minCMakeVersion = args.minCMakeVersion
        self.projectName = args.projectName
        self.cxxVersion = args.cppVersion
        self.defaultTargetType = args.defaultTargetType

    def generateCMakeFileContent(self):
        strIO = StringIO()

        strIO.write("set(PROJECT_NAME \"" + self.projectName + "\")\n")
        strIO.write("project(${PROJECT_NAME} CXX)\n")
        strIO.write("\n")
        strIO.write("set(CMAKE_CXX_STANDARD " + self.cxxVersion + ")\n")
        strIO.write("\n")
        strIO.write("#add_definitions(\"-DDEVELOPMENT_BUILD\")\n")
        strIO.write("set(" + self.projectName.upper() + "_PUBLIC_HEADERS \"" + \
               join(join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubHeaders"][len(self.projectName) + 1:]), self.projectName.lower()) + ".h\")\n")
        strIO.write("set(" + self.projectName.upper() + "_PRIVATE_HEADERS \"" + join("${CMAKE_CURRENT_LIST_DIR}", self.paths["privHeaders"][len(self.projectName) + 1:]) + "\")\n")
        strIO.write("set(" + self.projectName.upper() + "_SRC \"" + join(join("${CMAKE_CURRENT_LIST_DIR}", self.paths["src"][len(self.projectName) + 1:]), self.projectName.lower()) + ".cpp\")\n")
        strIO.write("\n")

        if self.defaultTargetType == "lib":
            strIO.write("add_library(${PROJECT_NAME} "
                                                 + " ${" + self.projectName.upper() + "_SRC}" \
                                                 + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                                                 + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                                                 + ")\n")
            strIO.write("install(TARGETS \"${PROJECT_NAME}\" DESTINATION \"/usr/local/lib/\" PUBLIC_HEADER DESTINATION \"/usr/local/include/" + self.projectName + "/\" COMPONENT \"${PROJECT_NAME}\")\n")
        else:
            strIO.write("add_executable(${PROJECT_NAME} "
                                                 + " ${" + self.projectName.upper() + "_SRC}" \
                                                 + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                                                 + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                                                 + ")\n")
            strIO.write("install(TARGETS \"${PROJECT_NAME}\" DESTINATION \"/usr/local/bin/\" PUBLIC_HEADER DESTINATION \"/usr/local/include/" + self.projectName + "/\" COMPONENT \"${PROJECT_NAME}\")\n")

        strIO.write("target_include_directories(${PROJECT_NAME} PUBLIC \"" + \
                    join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubInc"][len(self.projectName) + 1:]) + "\")")

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

    docs = join(base, "documentation")

    code = join(base, "code")
    pub = join(code, "public")
    priv = join(code, "private")
    pubInc = join(pub, "include")
    privInc = join(priv, "include")
    pubHeaders = join(pubInc, base.lower())
    privHeaders = join(privInc, base.lower())
    src = join(code, "src")
    test = join(code, "test")

    paths = { "base": base, "docs": docs, "code" : code, "pub" : pub, "priv" : priv,\
              "pubHeaders" : pubHeaders, "privHeaders" : privHeaders, "src" : src, \
              "pubInc" : pubInc, "privInc" : privInc, "test": test}

    for name, d in paths.items():
        os.makedirs(d, 0o755, True)

    return paths


def generateCMakeFiles(paths, args):
    cmakeGenerator = MainCMakeGenerator(args, paths)

    f = open(join(paths["base"], MainCMakeGenerator.CMakeFileName), "w")
    f.write(cmakeGenerator.generateCMakeFileContent())
    f.close()


def generateDefaultSourceFiles(paths, args):
    f = open(join(paths["pubHeaders"], args.projectName.lower()) + ".h", "w")
    f.write("#ifndef " + args.projectName.upper() + "_H\n")
    f.write("#define " + args.projectName.upper() + "_H\n\n")
    f.write("#endif\n\n")
    f.close()

    f = open(join(paths["src"], args.projectName.lower()) + ".cpp", "w")
    f.write("#include \"" + join(args.projectName.lower(), args.projectName.lower()) + ".h\"\n")
    f.close()


def generateMakeScript(paths, args):
    f = open(join(paths["base"], "build.sh"), "w")
    f.write("#!/bin/bash\n\n")
    f.write("echo \"Building: " + args.projectName + "\";\n")
    f.write("PROJECT_PATH=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\"\n")
    f.write(". ${PROJECT_PATH}/../baseEnvironment.sh;\n\n")
    f.write("pushd \"" + join("${BUILD_ROOT}", args.projectName) + "\";\n")
    f.write("cmake \"${PROJECT_PATH}\";\n")
    f.write("make;\n")
    f.write("popd;\n")
    f.close()


if __name__ == "__main__":
    print("Generating your project!\n")

    argParser = argparse.ArgumentParser(description="Generates the base structure of a new c++ project.")
    argParser.add_argument("projectName", help="The name of your new project.")
    argParser.add_argument("--cppVersion", help="The c++ standard that the project should use. Default is 14.", choices=["03","11","14","17"], default="14")
    argParser.add_argument("--minCMakeVersion", default="3.8.2", help="CMake version requirement.")
    argParser.add_argument("--defaultTargetType", choices=["lib", "exec"], default="lib", help="The type of target that will be built in the project(library, executable). Default value is library.")
    args = argParser.parse_args()

    paths = generatePaths(args)
    generateCMakeFiles(paths, args)
    generateMakeScript(paths, args)
    generateDefaultSourceFiles(paths, args)
