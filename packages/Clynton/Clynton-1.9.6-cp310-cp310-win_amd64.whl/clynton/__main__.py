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
"""
This is the main program of Clynton, it checks the options and then translates
one or more modules to a C source code using Python C/API in a "*.build"
directory and then compiles that to either an executable or an extension module
or package, that can contain all used modules too.
"""

# Note: This avoids imports at all costs, such that initial startup doesn't do more
# than necessary, until re-execution has been decided.

import os
import sys


def main():
    # PyLint for Python3 thinks we import from ourselves if we really
    # import from package, pylint: disable=I0021,no-name-in-module

    # Also high complexity.
    # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    if (
        os.name == "nt"
        and os.path.normcase(os.path.basename(sys.executable)) == "pythonw.exe"
    ):
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            None,
            "You have to use the 'python.exe' and not a 'pythonw.exe' to run Clynton",
            "Error",
            0x1000,  # MB_SYSTEMMODAL
        )
        sys.exit(1)

    if "CLYNTON_BINARY_NAME" in os.environ:
        sys.argv[0] = os.environ["CLYNTON_BINARY_NAME"]

    if "CLYNTON_PYTHONPATH" in os.environ:
        # Restore the PYTHONPATH gained from the site module, that we chose not
        # to have imported during compilation. For loading ast module, we need
        # one element, that is not necessarily in our current path.
        sys.path = [os.environ["CLYNTON_PYTHONPATH_AST"]]
        import ast

        sys.path = ast.literal_eval(os.environ["CLYNTON_PYTHONPATH"])
        del os.environ["CLYNTON_PYTHONPATH"]
    else:
        # Remove path element added for being called via "__main__.py", this can
        # only lead to trouble, having e.g. a "distutils" in sys.path that comes
        # from "clynton.distutils".
        sys.path = [
            path_element
            for path_element in sys.path
            if os.path.dirname(os.path.abspath(__file__)) != path_element
        ]

    # We will run with the Python configuration as specified by the user, if it does
    # not match, we restart ourselves with matching configuration.
    needs_re_execution = False

    if sys.flags.no_site == 0:
        needs_re_execution = True

    # The hash randomization totally changes the created source code created,
    # changing it every single time Clynton is run. This kills any attempt at
    # caching it, and comparing generated source code. While the created binary
    # actually may still use it, during compilation we don't want to. So lets
    # disable it.
    if os.environ.get("PYTHONHASHSEED", "-1") != "0":
        needs_re_execution = True

    # Avoid doing it when running in Visual Code.
    if needs_re_execution and "debugpy" in sys.modules:
        needs_re_execution = False

    # In case we need to re-execute.
    if needs_re_execution:
        from clynton.utils.ReExecute import reExecuteClynton  # isort:skip

        # Does not return
        reExecuteClynton(pgo_filename=None)

    # We don't care about deprecations in any version, and these are triggered
    # by run time calculations of "range" and others, while on python2.7 they
    # are disabled by default.
    import warnings

    warnings.simplefilter("ignore", DeprecationWarning)

    from clynton import Options  # isort:skip

    Options.parseArgs()

    Options.commentArgs()

    # Load plugins after we know, we don't execute again.
    from clynton.plugins.Plugins import activatePlugins

    activatePlugins()

    if Options.isShowMemory():
        from clynton.utils import MemoryUsage

        MemoryUsage.startMemoryTracing()

    if "CLYNTON_NAMESPACES" in os.environ:
        # Restore the detected name space packages, that were force loaded in
        # site.py, and will need a free pass later on
        from clynton.importing.PreloadedPackages import setPreloadedPackagePaths

        setPreloadedPackagePaths(ast.literal_eval(os.environ["CLYNTON_NAMESPACES"]))
        del os.environ["CLYNTON_NAMESPACES"]

    if "CLYNTON_PTH_IMPORTED" in os.environ:
        # Restore the packages that the ".pth" files asked to import.
        from clynton.importing.PreloadedPackages import setPthImportedPackages

        setPthImportedPackages(ast.literal_eval(os.environ["CLYNTON_PTH_IMPORTED"]))
        del os.environ["CLYNTON_PTH_IMPORTED"]

    # Now the real main program of Clynton can take over.
    from clynton import MainControl  # isort:skip

    MainControl.main()

    if Options.isShowMemory():
        MemoryUsage.showMemoryTrace()


if __name__ == "__main__":
    if "CLYNTON_PACKAGE_HOME" in os.environ:
        sys.path.insert(0, os.environ["CLYNTON_PACKAGE_HOME"])

        import clynton  # just to have it loaded from there, pylint: disable=unused-import

        del sys.path[0]

    main()
