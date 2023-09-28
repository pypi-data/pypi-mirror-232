#!/usr/bin/python
#     Copyright 2023, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Clynton", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
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

""" Run a construct based comparison test.

This executes a program with and without snippet of code and
stores the numbers about it, extracted with Valgrind for use
in comparisons.

"""

import hashlib
import os
import sys
from optparse import OptionParser

from clynton.tools.testing.Common import (
    check_output,
    convertUsing2to3,
    decideNeeds2to3,
    getPythonSysPath,
    getPythonVersionString,
    getTempDir,
    my_print,
    setup,
)
from clynton.tools.testing.Constructs import generateConstructCases
from clynton.tools.testing.Valgrind import runValgrind
from clynton.utils.Execution import check_call
from clynton.utils.FileOperations import (
    copyFile,
    getFileContentByLine,
    getFileContents,
    putTextFileContents,
)


def _setPythonPath(case_name):
    if "Numpy" in case_name:
        os.environ["PYTHONPATH"] = getPythonSysPath()


def main():
    # Complex stuff, not broken down yet
    # pylint: disable=too-many-branches,too-many-locals,too-many-statements

    parser = OptionParser()

    parser.add_option(
        "--clynton", action="store", dest="clynton", default=os.environ.get("CLYNTON", "")
    )

    parser.add_option(
        "--cpython",
        action="store",
        dest="cpython",
        default=os.environ.get("PYTHON", sys.executable),
    )

    parser.add_option("--code-diff", action="store", dest="diff_filename", default="")

    parser.add_option("--copy-source-to", action="store", dest="target_dir", default="")

    options, positional_args = parser.parse_args()

    if len(positional_args) != 1:
        sys.exit("Error, need to give test case file name as positional argument.")

    test_case = positional_args[0]

    if os.path.exists(test_case):
        test_case = os.path.abspath(test_case)

    case_name = os.path.basename(test_case)

    if options.cpython == "no":
        options.cpython = ""

    clynton = options.clynton

    if os.path.exists(clynton):
        clynton = os.path.abspath(clynton)
    elif clynton:
        sys.exit("Error, clynton binary '%s' not found." % clynton)

    diff_filename = options.diff_filename
    if diff_filename:
        diff_filename = os.path.abspath(diff_filename)

    setup(silent=True, go_main=False)

    _setPythonPath(case_name)

    assert os.path.exists(test_case), (test_case, os.getcwd())

    my_print("PYTHON='%s'" % getPythonVersionString())
    my_print("PYTHON_BINARY='%s'" % os.environ["PYTHON"])
    my_print(
        "TEST_CASE_HASH='%s'"
        % hashlib.md5(getFileContents(test_case, "rb")).hexdigest()
    )

    needs_2to3 = decideNeeds2to3(test_case)

    if options.target_dir:
        copyFile(
            test_case, os.path.join(options.target_dir, os.path.basename(test_case))
        )

    # First produce two variants.
    temp_dir = getTempDir()

    test_case_1 = os.path.join(temp_dir, "Variant1_" + os.path.basename(test_case))
    test_case_2 = os.path.join(temp_dir, "Variant2_" + os.path.basename(test_case))

    case_1_source, case_2_source = generateConstructCases(getFileContents(test_case))

    putTextFileContents(test_case_1, case_1_source)
    putTextFileContents(test_case_2, case_2_source)

    if needs_2to3:
        test_case_1, _needs_delete = convertUsing2to3(test_case_1)
        test_case_2, _needs_delete = convertUsing2to3(test_case_2)

    os.environ["PYTHONHASHSEED"] = "0"

    if clynton:
        clynton_id = check_output(
            "cd %s; git rev-parse HEAD" % os.path.dirname(clynton), shell=True
        )
        clynton_id = clynton_id.strip()

        if sys.version_info > (3,):
            clynton_id = clynton_id.decode()

        my_print("CLYNTON_COMMIT='%s'" % clynton_id)

    os.chdir(getTempDir())

    if clynton:
        clynton_call = [
            os.environ["PYTHON"],
            clynton,
            "--quiet",
            "--no-progressbar",
            "--nofollow-imports",
            "--python-flag=no_site",
        ]

        clynton_call.extend(os.environ.get("CLYNTON_EXTRA_OPTIONS", "").split())

        clynton_call.append(case_name)

        # We want to compile under the same filename to minimize differences, and
        # then copy the resulting files afterwards.
        copyFile(test_case_1, case_name)

        check_call(clynton_call)

        if os.path.exists(case_name.replace(".py", ".exe")):
            exe_suffix = ".exe"
        else:
            exe_suffix = ".bin"

        os.rename(
            os.path.basename(test_case).replace(".py", ".build"),
            os.path.basename(test_case_1).replace(".py", ".build"),
        )
        os.rename(
            os.path.basename(test_case).replace(".py", exe_suffix),
            os.path.basename(test_case_1).replace(".py", exe_suffix),
        )

        copyFile(test_case_2, os.path.basename(test_case))

        check_call(clynton_call)

        os.rename(
            os.path.basename(test_case).replace(".py", ".build"),
            os.path.basename(test_case_2).replace(".py", ".build"),
        )
        os.rename(
            os.path.basename(test_case).replace(".py", exe_suffix),
            os.path.basename(test_case_2).replace(".py", exe_suffix),
        )

        if diff_filename:
            suffixes = [".c", ".cpp"]

            for suffix in suffixes:
                cpp_1 = os.path.join(
                    test_case_1.replace(".py", ".build"), "simplefile.__main__" + suffix
                )

                if os.path.exists(cpp_1):
                    break
            else:
                assert False

            for suffix in suffixes:
                cpp_2 = os.path.join(
                    test_case_2.replace(".py", ".build"), "simplefile.__main__" + suffix
                )
                if os.path.exists(cpp_2):
                    break
            else:
                assert False

            import difflib

            putTextFileContents(
                diff_filename,
                difflib.HtmlDiff().make_table(
                    getFileContentByLine(cpp_1),
                    getFileContentByLine(cpp_2),
                    "Construct",
                    "Baseline",
                    True,
                ),
            )

        clynton_1 = runValgrind(
            "Clynton construct",
            "callgrind",
            (test_case_1.replace(".py", exe_suffix),),
            include_startup=True,
        )

        clynton_2 = runValgrind(
            "Clynton baseline",
            "callgrind",
            (test_case_2.replace(".py", exe_suffix),),
            include_startup=True,
        )

        clynton_diff = clynton_1 - clynton_2

        my_print("CLYNTON_COMMAND='%s'" % " ".join(clynton_call), file=sys.stderr)
        my_print("CLYNTON_RAW=%s" % clynton_1)
        my_print("CLYNTON_BASE=%s" % clynton_2)
        my_print("CLYNTON_CONSTRUCT=%s" % clynton_diff)

    if options.cpython:
        os.environ["PYTHON"] = options.cpython

        cpython_call = [os.environ["PYTHON"], "-S", test_case_1]

        cpython_1 = runValgrind(
            "CPython construct",
            "callgrind",
            cpython_call,
            include_startup=True,
        )

        cpython_call = [os.environ["PYTHON"], "-S", test_case_2]

        cpython_2 = runValgrind(
            "CPython baseline",
            "callgrind",
            cpython_call,
            include_startup=True,
        )

        cpython_diff = cpython_1 - cpython_2

        my_print("CPYTHON_RAW=%d" % cpython_1)
        my_print("CPYTHON_BASE=%d" % cpython_2)
        my_print("CPYTHON_CONSTRUCT=%d" % cpython_diff)

    if options.cpython and options.clynton:
        if clynton_diff == 0:
            clynton_gain = float("inf")
        else:
            clynton_gain = float(100 * cpython_diff) / clynton_diff

        my_print("CLYNTON_GAIN=%.3f" % clynton_gain)
        my_print("RAW_GAIN=%.3f" % (float(100 * cpython_1) / clynton_1))
        my_print("BASE_GAIN=%.3f" % (float(100 * cpython_2) / clynton_2))


if __name__ == "__main__":
    main()
