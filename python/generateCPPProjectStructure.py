#!/bin/python3

import os
import sys
import argparse
from os.path import join
from os import chmod
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
        strIO.write("list(APPEND CMAKE_MODULE_PATH \"${CMAKE_CURRENT_LIST_DIR}/../../../cmakeSearchModule/\")\n")
        strIO.write("#add_definitions(\"-DDEVELOPMENT_BUILD\")\n\n\n")
        strIO.write("set(" + self.projectName.upper() + "_PUBLIC_HEADERS \"" + \
               join(join("${CMAKE_CURRENT_LIST_DIR}", self.paths["pubHeaders"][len(self.projectName) + 1:]), self.projectName.lower()) + ".h\")\n")
        strIO.write("set(" + self.projectName.upper() + "_PRIVATE_HEADERS \"" + join("${CMAKE_CURRENT_LIST_DIR}", self.paths["privHeaders"][len(self.projectName) + 1:]) + "\")\n")
        strIO.write("set(" + self.projectName.upper() + "_SRC \"" + join(join("${CMAKE_CURRENT_LIST_DIR}", self.paths["src"][len(self.projectName) + 1:]), self.projectName.lower()) + ".cpp\")\n")
        strIO.write("\n")

        targetDestination="bin"
        if self.defaultTargetType == "lib":
            strIO.write("add_library(${PROJECT_NAME} "
                             + " ${" + self.projectName.upper() + "_SRC}" \
                             + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                             + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                             + ")\n")
            targetDestination="lib"

            strIO.write("if(BUILD_SHARED_LIBS)\n")
            strIO.write("   set(INSTALL_TARGET_TYPE \"LIBRARY\")\n")
            strIO.write("else()\n")
            strIO.write("   set(INSTALL_TARGET_TYPE \"ARCHIVE\")\n")
            strIO.write("endif()\n")
        else:
            strIO.write("add_executable(${PROJECT_NAME} "
                             + " ${" + self.projectName.upper() + "_SRC}" \
                             + " ${" + self.projectName.upper() + "_PUBLIC_HEADERS}" \
                             + " ${" + self.projectName.upper() + "_PRIVATE_HEADERS}" \
                             + ")\n")
            strIO.write("set(INSTALL_TARGET_TYPE \"\")\n")

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


class TestCMakeGenerator():
    def __init__(self, args, paths):
        self.paths = paths
        self.minCMakeVersion = args.minCMakeVersion
        self.projectName = args.projectName
        self.cxxVersion = args.cppVersion
        self.defaultTargetType = args.defaultTargetType

    def generateCMakeFileContent(self):
        from io import StringIO
        strIO = StringIO()

        strIO.write("""
include("${CMAKE_CURRENT_LIST_DIR}/../../CMakeLists.txt")

cmake_minimum_required(VERSION 3.8.2)\n""")
        strIO.write("set(PROJECT_NAME \"" + self.projectName + "_test\")\n")
        strIO.write("""
project(${PROJECT_NAME} CXX)

set(CMAKE_CXX_STANDARD 14)

set(TEST_SOURCES "main.cpp")
add_executable(${PROJECT_NAME} ${TEST_SOURCES})

find_package(google_test REQUIRED)

set(LIBS "${google_test_LIBRARIES}" "pthread")
target_link_libraries(${PROJECT_NAME} ${LIBS})
target_include_directories(${PROJECT_NAME} PRIVATE ${google_test_INCLUDE_DIRS})
""")
        return strIO.getvalue()


def generateDefaultEnvironmentScript(paths):
    f = open(join(paths["scriptRes"], "defaultBaseEnvironment.sh"), "w")
    f.write("#!/bin/bash\n\n")
    f.write("export BASE_ENVIRONMENT_SCRIPT_PATH=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\";\n")
    f.write("export BUILD_ROOT=\"${BASE_ENVIRONMENT_SCRIPT_PATH}/../../../build/\";\n")
    f.write("export INSTALL_PREFIX=\"${BASE_ENVIRONMENT_SCRIPT_PATH}/../../../sysroot/\";\n")
    f.write("export PROJECT_ROOT=\"${BASE_ENVIRONMENT_SCRIPT_PATH}/../../../\";\n")
    f.close()
    chmod(f.name, 0o770)


def generateDefaultInitProjectScript(paths, args):
    f = open(join(paths["scriptRes"], "defaultInitProject.sh"), "w")
    f.write("#!/bin/bash\n")
    f.write("SCRIPT_PATH=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\";\n")
    f.write(". ${SCRIPT_PATH}/defaultBaseEnvironment.sh;\n")
    f.write("mkdir -p \"${BUILD_ROOT}\";\n")
    f.write("mkdir -p \"${INSTALL_PREFIX}\";\n")

    projectPath = join("${PROJECT_ROOT}", args.projectName)

    f.write("cp " + join("${PROJECT_ROOT}", join(paths["configRes"], ".clang-format"))+ "  \"" + projectPath  + "\";\n")
    f.write("cp " + join("${PROJECT_ROOT}", join(paths["configRes"], ".gitignore"))+ "  \"" + projectPath + "\";\n\n")
    f.write("cp " + join("${PROJECT_ROOT}", join(paths["configRes"], ".gitmessage"))+ "  \"" + projectPath  + "\";\n\n")

    f.write("pushd \"" + projectPath + "\" &> /dev/null;\n")
    f.write("mkdir -p .git/hooks;\n")

    f.write("printf \"[user]\\n\\tname = Szilard Orban\\n\\temail = devszilardo@gmail.com\\n\" > ./.git/config \n")
    f.write("printf \"[commit]\\n\\ttemplate = \\\"" + join(projectPath, ".gitmessage") + "\\\"\\n\" >> ./.git/config \n")
    f.write("printf \"[diff]\\n\\talgorithm = minimal\\n\\tmnemonicprefix = true\\n\" >> ./.git/config \n")
    f.write("printf \"[core]\\n\\teditor = vim\\n\" >> ./.git/config \n")
    f.write("git init;\n")
    f.write("git add .;\n")
    f.write("git commit -m \"Basic project structure\";\n")
    f.write("cp " + join("${PROJECT_ROOT}", join(paths["configRes"], "pre-commit"))+ " \"" + join(projectPath, ".git/hooks/") + "\";\n")
    f.write("popd &> /dev/null;\n")
    f.close()
    chmod(f.name, 0o770)


def generateGitPreCommitHook(paths):
    f = open(join(paths["configRes"], "pre-commit"), "w")
    f.write("""
#!/bin/bash

echo "Starting git pre-commit hook:";
projectRoot="$(dirname $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd))";
projectRoot=${projectRoot%/*};

## Check source code format
gitTmpName=".xgitTmp";
stagedFiles="`git diff --staged --name-only`";
currentBranchName="`git rev-parse --abbrev-ref HEAD`";

mkdir -p "${gitTmpName}";
success=1;
for stagedFile in `git diff --diff-filter=MCUBTAXR --staged --name-only | grep -E "\.h$|\.cpp$|\.c$|\.hpp$|\.cxx"`; do
    mkdir -p $(dirname "${gitTmpName}/${stagedFile}");
    git show :"${stagedFile}" | clang-format -style=file > "${gitTmpName}/${stagedFile}";
    originalHash=`git show :"${stagedFile}" | md5sum | cut -d " " -f 1`;
    formattedHash=`md5sum "${gitTmpName}/${stagedFile}" | cut -d " " -f 1`;
    if [ "${originalHash}" != "${formattedHash}" ]; then
        echo "${stagedFile}";
        success=0;
    fi
done

rm -rf "${gitTmpName}";
if [ "$success" -eq 0 ]; then
    echo "NOO! The above files were not formatted correctly, please run clang-format with the appropriate settings before attempting a commit!";
    exit 255;
fi

echo "Pre-commit hook passed successfully!";
exit 0;\n
""")
    f.close()
    chmod(f.name, 0o770)


def generateGitMessage(paths):
    f = open(join(paths["configRes"], ".gitmessage"), "w")
    f.write("######################################### Short Description [ 80 chars max ] ###########################################\n")
    f.write("#================================ 80 characters ================================#                                      #\n")
    f.write("## Short description about the change topic. Should be made on a single line.                                         ##\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("##                                                                                                                    ##\n")
    f.write("##################################### Detailed Description [ 120 chars per line ]  #####################################\n")
    f.write("#=================================================== 120 characters ===================================================#\n")
    f.write("## A more detailed description of what the change is meant to do, and why it is necessary.                            ##\n")
    f.write("## If the changes are related to any issues that are tracked in some system, the tracking ids should be placed on     ##\n")
    f.write("## the first line of the detailed description, between square brackets. If multiple ids are present, separate each    ##\n")
    f.write("## bracket enclosed id with a comma.                                                                                  ##\n")
    f.write("##                                                                                                                    ##\n")
    f.write("## Example:                                                                                                           ##\n")
    f.write("# Increase the foo concentration in the fleeb                                                                         ##\n")
    f.write("#                                              -- EMPTY LINE --                                                       ##\n")
    f.write("# [1415], [WRT-1941], [UBA-101]                                                                                       ##\n")
    f.write("# * Implemented the optional foo-pouch, to allow the fleeb to contain a higher dose of foo.                           ##\n")
    f.write("# * Added more foo to the fleeb. Increasing the foo concentration will allow us to transfer the mula with increased   ##\n")
    f.write("# efficiency.                                                                                                         ##\n")
    f.write("*\n")
    f.write("\n")
    f.write("\n")
    f.write("##                                                                                                                    ##\n")
    f.write("########################################################################################################################\n")
    f.close()


def generateGitIgnore(paths):
    f = open(join(paths["configRes"], ".gitignore"), "w")
    f.write(".DS_Store\n")
    f.write(".*.swp")
    f.write("*.slo\n")
    f.write("*.pch\n")
    f.write("*.gch\n")
    f.write("*.obj\n")
    f.write("*.o\n")
    f.write("*.pdb\n")
    f.write("*.idb\n")
    f.write("CMakeScripts\n")
    f.write("cmake_install.cmake\n")
    f.write("CMakeCache.txt\n")
    f.write("CMakeFiles\n")
    f.write("install_manifest.txt\n")
    f.write("compile_commands.json\n")
    f.write("*.suo\n")
    f.write("*.user\n")
    f.write("*.userosscache\n")
    f.write("*.sln.docstates\n")
    f.write(".qmake.stash\n")
    f.write(".qmake.cache\n")
    f.write("CMakeLists.txt.user.*\n")
    f.write("*.pro.user\n")
    f.write("*.moc\n")
    f.write("moc_*.cpp\n")
    f.write("moc_*.h\n")
    f.write("qrc_*.cpp\n")
    f.write("ui_*.h\n")
    f.write("*.qbs.user.*\n")
    f.write("*.qbs.user\n")
    f.close()


def generateDefaultClangFormatConfig(paths):
    f = open(join(paths["configRes"], ".clang-format"), "w")
    f.write("---\n" +
        "Language:        Cpp\n" +
        "AccessModifierOffset: -4\n" +
        "AlignAfterOpenBracket: Align\n" +
        "# AlignEscapedNewlines: Left\n" +
        "AlignOperands:   true\n" +
        "AlignTrailingComments: true\n" +
        "AllowAllParametersOfDeclarationOnNextLine: true\n" +
        "AllowShortBlocksOnASingleLine: false\n" +
        "AllowShortCaseLabelsOnASingleLine: false\n" +
        "AllowShortIfStatementsOnASingleLine: false\n" +
        "AllowShortLoopsOnASingleLine: false\n" +
        "AllowShortFunctionsOnASingleLine: Empty\n" +
        "AlwaysBreakAfterDefinitionReturnType: None\n" +
        "AlwaysBreakTemplateDeclarations: true\n" +
        "AlwaysBreakBeforeMultilineStrings: false\n" +
        "BraceWrapping: {\n" +
        "AfterClass: true,\n" +
        "AfterControlStatement: true,\n" +
        "AfterEnum: true,\n" +
        "AfterFunction: true,\n" +
        "AfterNamespace: true,\n" +
        "AfterStruct: true,\n" +
        "AfterUnion: true,\n" +
        "BeforeCatch: true,\n" +
        "BeforeElse: true,\n" +
        "IndentBraces: false,\n" +
        "}\n" +
        "# SplitEmptyFunctionBody: false\n" +
        "BreakBeforeBinaryOperators: None\n" +
        "# BreakBeforeInheritanceComma: true\n" +
        "BreakBeforeTernaryOperators: false\n" +
        "# BreakConstructorInitializers: BeforeComma\n" +
        "BinPackParameters: false\n" +
        "BinPackArguments: false\n" +
        "BreakStringLiterals: true\n" +
        "ColumnLimit:     120\n" +
        "ConstructorInitializerAllOnOneLineOrOnePerLine: true\n" +
        "ConstructorInitializerIndentWidth: 4\n" +
        "# CompactNamespaces: false\n" +
        "DerivePointerAlignment: false\n" +
        "ExperimentalAutoDetectBinPacking: false\n" +
        "# FixNamespaceComments: true\n" +
        "IndentCaseLabels: true\n" +
        "IndentWrappedFunctionNames: false\n" +
        "IndentFunctionDeclarationAfterType: false\n" +
        "MaxEmptyLinesToKeep: 1\n" +
        "KeepEmptyLinesAtTheStartOfBlocks: false\n" +
        "NamespaceIndentation: All\n" +
        "ObjCBlockIndentWidth: 2\n" +
        "ObjCSpaceAfterProperty: false\n" +
        "ObjCSpaceBeforeProtocolList: true\n" +
        "PenaltyBreakBeforeFirstCallParameter: 510\n" +
        "PenaltyBreakComment: 300\n" +
        "PenaltyBreakString: 310\n" +
        "PenaltyBreakFirstLessLess: 410\n" +
        "PenaltyExcessCharacter: 1000000\n" +
        "PenaltyReturnTypeOnItsOwnLine: 60\n" +
        "PointerAlignment: Left\n" +
        "SpacesBeforeTrailingComments: 1\n" +
        "Cpp11BracedListStyle: true\n" +
        "Standard:        Cpp11\n" +
        "IndentWidth:     4\n" +
        "ReflowComments: true\n" +
        "TabWidth:        4\n" +
        "SortIncludes: true\n" +
        "# SortUsingDeclarations: false\n" +
        "UseTab:          Never\n" +
        "BreakBeforeBraces: Custom\n" +
        "SpacesInParentheses: false\n" +
        "SpacesInSquareBrackets: false\n" +
        "SpacesInAngles:  false\n" +
        "SpaceInEmptyParentheses: false\n" +
        "SpacesInCStyleCastParentheses: false\n" +
        "SpaceAfterCStyleCast: true\n" +
        "SpaceAfterTemplateKeyword: false\n" +
        "SpacesInContainerLiterals: false\n" +
        "SpaceBeforeAssignmentOperators: true\n" +
        "ContinuationIndentWidth: 4\n" +
        "CommentPragmas:  '^ CLANG pragma:'\n" +
        "ForEachMacros:   [ foreach, Q_FOREACH, BOOST_FOREACH ]\n" +
        "SpaceBeforeParens: ControlStatements\n" +
        "DisableFormat:   false\n" +
        "...\n")
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
    testCmakeGenerator = TestCMakeGenerator(args, paths)

    f = open(join(paths["base"], MainCMakeGenerator.CMakeFileName), "w")
    f.write(cmakeGenerator.generateCMakeFileContent())
    f.close()

    f = open(join(paths["test"], MainCMakeGenerator.CMakeFileName), "w")
    f.write(testCmakeGenerator.generateCMakeFileContent())
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

    f = open(join(paths["test"], "main.cpp"), "w")
    f.write("""
#include "gtest/gtest.h"

int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
""")
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
    f.write("""
cmake -DCMAKE_INSTALL_PREFIX:PATH=\"${INSTALL_PREFIX}\" -DBUILD_SHARED_LIBS:BOOL=ON -G Ninja \"${PROJECT_PATH}\";
configOk=$?;
ninja;
buildOk=$?;
ninja install;
installOk=$?;

if [ "$1" == "test" ]; then
mkdir -p ./test;
pushd test;
    cmake -DCMAKE_INSTALL_PREFIX:PATH="${INSTALL_PREFIX}" -DBUILD_SHARED_LIBS:BOOL=ON -G Ninja "${PROJECT_PATH}/code/test";
    testConfigOk=$?;
    ninja;
    testBuildOk=$?;
    ninja install;
    testInstallOk=$?;
popd;
echo "==== Build Tests finished, config: ${testConfigOk}, build: ${testBuildOk}, install: ${testInstallOk}!";
fi\n""")

    f.write("if [ \"${HAVE_CTIME}\" -eq \"0\" ]; then ctime -end " + args.projectName + ".ct; fi\n")
    f.write("if [ \"${HAVE_CTIME}\" -eq \"0\" ]; then ctime -stats " + args.projectName + ".ct; fi\n\n")

    f.write("popd 2&>1 /dev/null;\n\n")
    f.write("echo \"==== Build " + args.projectName + " finished, config: ${configOk}, build: ${buildOk}, install: ${installOk}!\";");
    f.close()
    chmod(f.name, 0o770)


if __name__ == "__main__":
    print("Generating your project!\n")

    argParser = argparse.ArgumentParser(description="Generates the base structure of a new c++ project.")
    argParser.add_argument("projectName", help="The alphanum name of your new project.")
    argParser.add_argument("--cppVersion", help="The c++ standard that the project should use. Default is 14.", choices=["03","11","14","17"], default="14")
    argParser.add_argument("--minCMakeVersion", default="3.8.2", help="CMake version requirement.")
    argParser.add_argument("--defaultTargetType", choices=["lib", "exec"], default="lib", help="The type of target that will be built in the project(library, executable). Default value is library.")
    args = argParser.parse_args()

    invalidNameTokens =  ["/", "\\", ":", ",", "<", ">", "[", "]", "{", "}", "|", "'", "\"", ";", "=", "+", "*", "!", "@", "#", "$", "%", "^", "&", "(", ")"]
    for invalidToken in invalidNameTokens:
        if invalidToken in args.projectName:
            print("Error: Invalid project name specified, please don't use any of the following characters: " + "".join(invalidNameTokens))
            print("       Try to use alphanum characters instead!")
            sys.exit(-1)

    paths = generatePaths(args)
    generateCMakeFiles(paths, args)
    generateMakeScript(paths, args)
    generateDefaultSourceFiles(paths, args)
    generateDefaultClangFormatConfig(paths)
    generateGitIgnore(paths)
    generateGitMessage(paths)
    generateGitPreCommitHook(paths)
    generateDefaultEnvironmentScript(paths)
    generateDefaultInitProjectScript(paths, args)
    print("Project generation finished..")
