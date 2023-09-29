#!/usr/bin/env python
#     Copyright 2023, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python tests originally created or extracted from other peoples work. The
#     parts were too small to be protected.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

""" Test Clynton compiling itself and compiling itself in compiled form again.

This should not only give no errors, but the same source for modules being
compiled when Clynton is running compiled and uncompiled, so we can discover
changes in order of execution in this test.
"""

import os
import sys

# Find clynton package relative to us.
sys.path.insert(
    0,
    os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    ),
)

# isort:start

import difflib
import shutil
import subprocess
import time

from clynton.tools.Basics import addPYTHONPATH
from clynton.tools.testing.Common import (
    getPythonSysPath,
    getTempDir,
    my_print,
    setup,
    test_logger,
    withPythonPathChange,
)
from clynton.utils.Execution import wrapCommandForDebuggerForSubprocess
from clynton.utils.FileOperations import (
    copyTree,
    deleteFile,
    listDir,
    removeDirectory,
)
from clynton.utils.Importing import getSharedLibrarySuffix
from clynton.Version import getCommercialVersion

clynton_main_path = os.path.join("..", "..", "bin", "clynton")

tmp_dir = getTempDir()

# Cannot detect this more automatic, so we need to list them, avoiding
# the ones not needed.
PACKAGE_LIST = [
    "clynton",
    "clynton/nodes",
    "clynton/specs",
    "clynton/nodes/shapes",
    "clynton/tree",
    "clynton/importing",
    "clynton/build",
    "clynton/freezer",
    "clynton/code_generation",
    "clynton/code_generation/templates",
    "clynton/code_generation/c_types",
    "clynton/optimizations",
    "clynton/finalizations",
    "clynton/plugins",
    "clynton/plugins/standard",
    "clynton/plugins/commercial",
    "clynton/reports",
    "clynton/pgo",
    "clynton/containers",
    "clynton/utils",
]

if not getCommercialVersion():
    PACKAGE_LIST.remove("clynton/plugins/commercial")

exe_suffix = ".exe" if os.name == "nt" else ".bin"


def readSource(filename):
    if str is bytes:
        return open(filename, "rb").read()
    else:
        return open(filename, "rb").read().decode("latin1")


def diffRecursive(dir1, dir2):
    # Complex in nature, pylint: disable=too-many-branches

    done = set()

    result = False

    for path1, filename in listDir(dir1):
        if "cache-" in path1:
            continue

        path2 = os.path.join(dir2, filename)

        done.add(path1)

        # Skip these binary files and scons build database of course.
        # TODO: Temporary ignore ".bin", until we have something better than marshal which behaves
        # differently in compiled Clynton:
        if filename.endswith(
            (
                ".o",
                ".os",
                ".obj",
                ".dblite",
                ".tmp",
                ".sconsign",
                ".txt",
                ".bin",
                ".const",
                ".exp",
            )
        ):
            continue

        if not os.path.exists(path2):
            test_logger.warning("Only in %s: %s" % (dir1, filename))
            result = False
            continue

        if os.path.isdir(path1):
            r = diffRecursive(path1, path2)
            if r:
                result = True
        elif os.path.isfile(path1):
            fromdate = time.ctime(os.stat(path1).st_mtime)
            todate = time.ctime(os.stat(path2).st_mtime)

            diff = difflib.unified_diff(
                a=readSource(path1).splitlines(),
                b=readSource(path2).splitlines(),
                fromfile=path1,
                tofile=path2,
                fromfiledate=fromdate,
                tofiledate=todate,
                n=3,
            )

            diff_list = list(diff)

            if diff_list:
                for line in diff_list:
                    try:
                        my_print(line)
                    except UnicodeEncodeError:
                        my_print(repr(line))

                result = True
        else:
            assert False, path1

    for path1, filename in listDir(dir2):
        if "cache-" in path1:
            continue

        path2 = os.path.join(dir2, filename)

        if path1 in done:
            continue

        if not os.path.exists(path1):
            test_logger.warning("Only in %s: %s" % (dir2, filename))
            result = False
            continue

    return result


def _traceCompilation(path, pass_number):
    test_logger.info("Compiling '%s' (PASS %d)." % (path, pass_number))


def executePASS1():
    test_logger.info(
        "PASS 1: Compiling to many compiled modules from compiler running from .py files."
    )

    base_dir = os.path.join("..", "..")

    for package in PACKAGE_LIST:
        package = package.replace("/", os.path.sep)

        source_dir = os.path.join(base_dir, package)
        target_dir = package

        removeDirectory(path=target_dir, ignore_errors=False)

        os.mkdir(target_dir)

        for path, filename in listDir(target_dir):
            if filename.endswith((".so", ".dylib")):
                os.unlink(path)

        for path, filename in listDir(source_dir):
            if not filename.endswith(".py"):
                continue

            if filename.startswith(".#"):
                continue

            if filename != "__init__.py":
                _traceCompilation(path=path, pass_number=1)

                command = [
                    os.environ["PYTHON"],
                    clynton_main_path,
                    "--module",
                    "--nofollow-imports",
                    "--output-dir=%s" % target_dir,
                    "--no-pyi-file",
                    path,
                ]
                command += os.environ.get("CLYNTON_EXTRA_OPTIONS", "").split()

                my_print("Command: ", " ".join(command))

                result = subprocess.call(command)

                if result != 0:
                    sys.exit(result)
            else:
                shutil.copyfile(path, os.path.join(target_dir, filename))

    _traceCompilation(path=clynton_main_path, pass_number=1)

    shutil.copyfile(clynton_main_path, "clynton-runner.py")

    command = [
        os.environ["PYTHON"],
        clynton_main_path,
        "--nofollow-imports",
        "--enable-plugin=pylint-warnings",
        "--output-dir=.",
        "--python-flag=no_site",
        "clynton-runner.py",
    ]
    command += os.environ.get("CLYNTON_EXTRA_OPTIONS", "").split()

    my_print("Command: ", " ".join(command))
    result = subprocess.call(command)

    if result != 0:
        sys.exit(result)

    shutil.move("clynton-runner" + exe_suffix, "clynton" + exe_suffix)

    scons_inline_copy_path = os.path.join(base_dir, "clynton", "build", "inline_copy")

    if os.path.exists(scons_inline_copy_path):
        copyTree(scons_inline_copy_path, os.path.join("clynton", "build", "inline_copy"))

    # Copy required data files.
    for filename in (
        "clynton/build/randomBack.scons",
        "clynton/plugins/standard/standard.clynton-package.config.yml",
        "clynton/plugins/standard/stdlib3.clynton-package.config.yml",
        "clynton/plugins/standard/stdlib2.clynton-package.config.yml",
    ):
        shutil.copyfile(
            os.path.join(base_dir, filename),
            filename,
        )

    copyTree(
        os.path.join(base_dir, "clynton", "code_generation", "templates_c"),
        os.path.join("clynton", "code_generation", "templates_c"),
    )

    copyTree(
        os.path.join(base_dir, "clynton", "build", "stat_source"),
        os.path.join("clynton", "build", "stat_source"),
    )
    copyTree(
        os.path.join(base_dir, "clynton", "build", "include"),
        os.path.join("clynton", "build", "include"),
    )

    # The data composer tool, use it by source.
    copyTree(
        os.path.join(base_dir, "clynton", "tools"),
        os.path.join("clynton", "tools"),
    )

    test_logger.info("OK.")


def compileAndCompareWith(clynton, pass_number):
    if "PYTHONHASHSEED" not in os.environ:
        os.environ["PYTHONHASHSEED"] = "0"

    base_dir = os.path.join("..", "..")

    for package in PACKAGE_LIST:
        package = package.replace("/", os.path.sep)

        source_dir = os.path.join(base_dir, package)

        for path, filename in listDir(source_dir):
            if not filename.endswith(".py"):
                continue

            if filename.startswith(".#"):
                continue

            path = os.path.join(source_dir, filename)

            if filename != "__init__.py":
                _traceCompilation(path=path, pass_number=pass_number)

                target = filename.replace(".py", ".build")

                target_dir = os.path.join(tmp_dir, target)

                removeDirectory(path=target_dir, ignore_errors=False)

                command = [
                    clynton,
                    "--module",
                    "--enable-plugin=pylint-warnings",
                    "--output-dir=%s" % tmp_dir,
                    "--no-pyi-file",
                    "--nofollow-imports",
                    path,
                ]
                command += os.environ.get("CLYNTON_EXTRA_OPTIONS", "").split()

                my_print("Command: ", " ".join(command))
                exit_clynton = subprocess.call(command)

                # In case of segfault or assertion triggered, run in debugger.
                if exit_clynton in (-11, -6) and sys.platform != "nt":
                    command2 = wrapCommandForDebuggerForSubprocess(*command)
                    subprocess.call(command2)

                if exit_clynton != 0:
                    my_print("An error exit %s occurred, aborting." % exit_clynton)
                    sys.exit(exit_clynton)

                has_diff = diffRecursive(os.path.join(package, target), target_dir)

                if has_diff:
                    sys.exit("There were differences!")

                shutil.rmtree(target_dir)

                for preferred in (True, False):
                    target_filename = filename.replace(
                        ".py", getSharedLibrarySuffix(preferred=preferred)
                    )

                    deleteFile(
                        path=os.path.join(tmp_dir, target_filename), must_exist=False
                    )


def executePASS2():
    test_logger.info(
        "PASS 2: Compiling from compiler running from entry '.exe' and many extension files."
    )

    with withPythonPathChange(getPythonSysPath()):
        # Windows will load the compiled modules (pyd) only from PYTHONPATH, so we
        # have to add it.
        if os.name == "nt":
            addPYTHONPATH(PACKAGE_LIST)

        compileAndCompareWith(
            clynton=os.path.join(".", "clynton" + exe_suffix), pass_number=2
        )

    test_logger.info("OK.")


def executePASS3():
    test_logger.info(
        "PASS 3: Compiling from compiler running from .py files to single .exe."
    )

    exe_path = os.path.join(tmp_dir, "clynton" + exe_suffix)

    if os.path.exists(exe_path):
        os.unlink(exe_path)

    build_path = os.path.join(tmp_dir, "clynton.build")

    if os.path.exists(build_path):
        shutil.rmtree(build_path)

    path = os.path.join("..", "..", "bin", "clynton")

    _traceCompilation(path=path, pass_number=3)

    command = [
        os.environ["PYTHON"],
        clynton_main_path,
        path,
        "--output-dir=%s" % tmp_dir,
        "--python-flag=-S",
        "--follow-imports",
    ]

    my_print("Command: ", " ".join(command))
    result = subprocess.call(command)

    if result != 0:
        sys.exit(result)

    shutil.rmtree(build_path)

    test_logger.info("OK.")


def executePASS4():
    test_logger.info("PASS 4: Compiling the compiler running from single exe.")

    exe_path = os.path.join(tmp_dir, "clynton" + exe_suffix)

    with withPythonPathChange(getPythonSysPath()):
        # Windows will load the compiled modules (pyd) only from PYTHONPATH, so we
        # have to add it.
        if os.name == "nt":
            addPYTHONPATH(PACKAGE_LIST)

        compileAndCompareWith(exe_path, pass_number=4)

    test_logger.info("OK.")


def executePASS5():
    my_print(
        "PASS 5: Compiling the compiler 'clynton' package to single extension module."
    )

    path = os.path.join("..", "..", "clynton")

    command = [
        os.environ["PYTHON"],
        clynton_main_path,
        "--enable-plugin=pylint-warnings",
        "--output-dir=%s" % tmp_dir,
        "--include-plugin-dir=%s" % path,
        "--nofollow-import-to=clynton.build.inline_copy",
        "--nofollow-import-to=clynton.build.include",
        "--nofollow-import-to=clynton.build.stat_source",
        "--nofollow-import-to=clynton.tools",
        "--module",
        path,
    ]

    result = subprocess.call(command)

    if result != 0:
        sys.exit(result)

    for preferred in True, False:
        candidate = "clynton" + getSharedLibrarySuffix(preferred=preferred)

        deleteFile(candidate, must_exist=False)

    os.unlink(os.path.join(tmp_dir, "clynton.pyi"))
    shutil.rmtree(os.path.join(tmp_dir, "clynton.build"))


def main():
    setup(needs_io_encoding=True)

    executePASS1()
    executePASS2()
    executePASS3()
    executePASS4()

    shutil.rmtree("clynton")

    executePASS5()


if __name__ == "__main__":
    main()
