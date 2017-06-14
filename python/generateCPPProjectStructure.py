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
        strIO.write("#add_definitions(\"-DDEVELOPMENT_BUILD\")\n\n\n")
        strIO.write("set(" + self.projectName.upper() + "_PUBLIC_HEADERS \"" + \
               join(join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubHeaders"][len(self.projectName) + 1:]), self.projectName.lower()) + ".h\")\n")
        strIO.write("set(" + self.projectName.upper() + "_PRIVATE_HEADERS \"" + join("${CMAKE_CURRENT_LIST_DIR}", self.paths["privHeaders"][len(self.projectName) + 1:]) + "\")\n")
        strIO.write("set(" + self.projectName.upper() + "_SRC \"" + join(join("${CMAKE_CURRENT_LIST_DIR}", self.paths["src"][len(self.projectName) + 1:]), self.projectName.lower()) + ".cpp\")\n")
        strIO.write("\n")

        targetDestination="bin"
        strIO.write("set(INSTALL_TARGET_TYPE \"\")\n")
        if self.defaultTargetType == "lib":
            strIO.write("add_library(${PROJECT_NAME} "
                             + " ${" + self.projectName.upper() + "_SRC}" \
                             + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                             + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                             + ")\n")
            targetDestination="lib"

            strIO.write("set(INSTALL_TARGET_TYPE \"ARCHIVE\")\n\n")
            strIO.write("if(BUILD_SHARED_LIBS)\n")
            strIO.write("   set(INSTALL_TARGET_TYPE \"LIBRARY\")\n")
            strIO.write("endif()\n")
        else:
            strIO.write("add_executable(${PROJECT_NAME} "
                             + " ${" + self.projectName.upper() + "_SRC}" \
                             + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                             + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                             + ")\n")

        strIO.write("set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER ${" + self.projectName.upper() + "_PUBLIC_HEADERS})\n")
        strIO.write("target_include_directories(${PROJECT_NAME} PUBLIC\n" + \
            "   $<BUILD_INTERFACE:" + join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubInc"][len(self.projectName) + 1:]) + ">\n" + \
            "   $<INSTALL_INTERFACE:" + join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubInc"][len(self.projectName) + 1:]) + ">\n" + \
            "   PRIVATE " + join("${CMAKE_CURRENT_LIST_DIR}", self.paths["privInc"][len(self.projectName) + 1:]) + \
            ")\n")
        strIO.write("install(TARGETS ${PROJECT_NAME} " + " ${INSTALL_TARGET_TYPE} DESTINATION \"" + targetDestination + "\" "+ \
                " PUBLIC_HEADER DESTINATION \"include/" + self.projectName + "\")\n")

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


def generateDefaultEnvironmentScript(paths):
    f = open(join(paths["scriptRes"], "defaultBaseEnvironment.sh"), "w")
    f.write("#!/bin/bash\n\n")
    f.write("export BASE_ENVIRONMENT_SCRIPT_PATH=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\";\n")
    f.write("export BUILD_ROOT=\"${BASE_ENVIRONMENT_SCRIPT_PATH}/../../../build/\";\n")
    f.write("export INSTALL_PREFIX=\"${BASE_ENVIRONMENT_SCRIPT_PATH}/../../../sysroot/\";\n")
    f.close()


def generateDefaultInitProjectScript(paths):
    f = open(join(paths["scriptRes"], "defaultInitProject.sh"), "w")
    f.write("#!/bin/bash\n")
    f.write("SCRIPT_PATH=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\";\n")
    f.write(". ${SCRIPT_PATH}/defaultBaseEnvironment.sh;\n")
    f.write("mkdir -p \"${BUILD_ROOT}\";\n")
    f.write("mkdir -p \"${INSTALL_PREFIX}\";\n")
    f.write("mv " + join(paths["configRes"], ".clang-format") + "  \"${BASE_ENVIRONMENT_SCRIPT_PATH}/../../\";\n")
    f.close()


def generateDefaultClangFormatConfig(paths):
    f = open(join(paths["configRes"], ".clang-format"), "w")
    f.write("---\n\
        Language:        Cpp\n\
        # BasedOnStyle:  WebKit\n\
        AccessModifierOffset: -4\n\
        AlignAfterOpenBracket: true\n\
        AlignEscapedNewlinesLeft: true\n\
        AlignOperands:   true\n\
        AlignTrailingComments: true\n\
        AllowAllParametersOfDeclarationOnNextLine: true\n\
        AllowShortBlocksOnASingleLine: false\n\
        AllowShortCaseLabelsOnASingleLine: false\n\
        AllowShortIfStatementsOnASingleLine: false\n\
        AllowShortLoopsOnASingleLine: false\n\
        AllowShortFunctionsOnASingleLine: Empty\n\
        AlwaysBreakAfterDefinitionReturnType: false\n\
        AlwaysBreakTemplateDeclarations: true\n\
        AlwaysBreakBeforeMultilineStrings: false\n\
        BreakBeforeBinaryOperators: NonAssignment\n\
        BreakBeforeTernaryOperators: false\n\
        BreakConstructorInitializersBeforeComma: true\n\
        BinPackParameters: false\n\
        BinPackArguments: false\n\
        ColumnLimit:     120\n\
        ConstructorInitializerAllOnOneLineOrOnePerLine: true\n\
        ConstructorInitializerIndentWidth: 4\n\
        DerivePointerAlignment: false\n\
        ExperimentalAutoDetectBinPacking: false\n\
        IndentCaseLabels: true\n\
        IndentWrappedFunctionNames: false\n\
        IndentFunctionDeclarationAfterType: false\n\
        MaxEmptyLinesToKeep: 1\n\
        KeepEmptyLinesAtTheStartOfBlocks: false\n\
        NamespaceIndentation: None\n\
        ObjCBlockIndentWidth: 2\n\
        ObjCSpaceAfterProperty: false\n\
        ObjCSpaceBeforeProtocolList: true\n\
        PenaltyBreakBeforeFirstCallParameter: 510\n\
        PenaltyBreakComment: 300\n\
        PenaltyBreakString: 310\n\
        PenaltyBreakFirstLessLess: 410\n\
        PenaltyExcessCharacter: 1000000\n\
        PenaltyReturnTypeOnItsOwnLine: 60\n\
        PointerAlignment: Left\n\
        SpacesBeforeTrailingComments: 1\n\
        Cpp11BracedListStyle: true\n\
        Standard:        Cpp11\n\
        IndentWidth:     4\n\
        TabWidth:        4\n\
        UseTab:          Never\n\
        BreakBeforeBraces: Allman\n\
        SpacesInParentheses: false\n\
        SpacesInSquareBrackets: false\n\
        SpacesInAngles:  false\n\
        SpaceInEmptyParentheses: false\n\
        SpacesInCStyleCastParentheses: false\n\
        SpaceAfterCStyleCast: true\n\
        SpacesInContainerLiterals: false\n\
        SpaceBeforeAssignmentOperators: true\n\
        ContinuationIndentWidth: 4\n\
        CommentPragmas:  '^ IWYU pragma:'\n\
        ForEachMacros:   [ foreach, Q_FOREACH, BOOST_FOREACH ]\n\
        SpaceBeforeParens: Never\n\
        DisableFormat:   false\n\
        ...\n")
    f.close()


def generatePaths(args):
    base = args.projectName

    docs = join(base, "documentation")

    resources = join(base, "resources")
    scriptRes = join(resources, "scripts")
    configRes = join(resources, "configs")

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
              "pubInc" : pubInc, "privInc" : privInc, "test": test, "resources" : resources, \
              "scriptRes" : scriptRes, "configRes" : configRes }

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
    f.write("mkdir -p \"" + join("${BUILD_ROOT}", args.projectName) + "\";\n")
    f.write("which ctime 2> /dev/null;\n")
    f.write("HAVE_CTIME=$?;\n\n")

    f.write("pushd \"" + join("${BUILD_ROOT}", args.projectName) + "\";\n\n")
    f.write("if [ \"${HAVE_CTIME}\" -eq \"0\" ]; then ctime -begin " + args.projectName + ".ct; fi\n")
    f.write("cmake -DCMAKE_INSTALL_PREFIX:PATH=\"${INSTALL_PREFIX}\" -G Ninja \"${PROJECT_PATH}\";\n")
    f.write("ninja;\n")
    f.write("ninja install;\n\n")

    f.write("if [ \"${HAVE_CTIME}\" -eq \"0\" ]; then ctime -end " + args.projectName + ".ct; fi\n")
    f.write("if [ \"${HAVE_CTIME}\" -eq \"0\" ]; then ctime -stats " + args.projectName + ".ct; fi\n\n")

    f.write("popd 2&>1 /dev/null;\n\n")

    f.write("echo \"Build finished!\";")
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
    generateDefaultEnvironmentScript(paths)
    generateDefaultInitProjectScript(paths)
    generateDefaultClangFormatConfig(paths)
