# -*- coding: utf-8 -*-

"""

test.test_commandline

Unit test the commandline module

Copyright (C) 2023 Rainer Schwarzbach

This file is part of glsr-present.

glsr-present is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

glsr-present is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import io

# import logging
import os
import tempfile

from unittest import TestCase

from unittest.mock import patch

from glsr_present import commandline

from .commons import GenericCallResult, RETURNCODE_OK


MOCK_TEMPLATE = """# Build information

_provided by [glsr-present](https://pypi.org/project/glsr-present/)
{{ version }} WITH A USER-SUPPLIED TEMPLATE_

[{{ build_info.ci_project_title }}]({{ build_info.ci_project_url }})
"""


class ExecResult(GenericCallResult):

    """Program execution result"""

    @classmethod
    def do_call(cls, *args, **kwargs):
        """Do the real function call"""
        program = commandline.Program(list(args))
        return program.execute()


class Program(TestCase):

    """Test the Program class"""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_execute(self, mock_stdout):
        """execute() method, returncode only"""
        with tempfile.TemporaryDirectory() as tempdir:
            result = ExecResult.from_call(
                "-o",
                tempdir,
                stdout=mock_stdout,
            )
        #
        self.assertEqual(result.returncode, RETURNCODE_OK)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list(self, mock_stdout):
        """execute() method, list templates"""
        result = ExecResult.from_call(
            "-l",
            stdout=mock_stdout,
        )
        self.assertIn(
            commandline.DEFAULT_BUILTIN_TEMPLATE,
            list(result.stdout.splitlines()),
        )

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_version(self, mock_stdout):
        """execute() method, version output"""
        with self.assertRaises(SystemExit) as cmgr:
            commandline.Program(["--version"]).execute()
        #
        self.assertEqual(cmgr.exception.code, RETURNCODE_OK)
        self.assertEqual(
            mock_stdout.getvalue().strip(),
            commandline.__version__,
        )

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_other_template(self, mock_stdout):
        """execute() method, different template"""
        mock_project_title = "glsr-test"
        mock_project_url = f"http://127.0.0.1/{mock_project_title}"
        with tempfile.TemporaryDirectory() as tempdir:
            template_file_name = f"{tempdir}/example.md.j2"
            with open(template_file_name, "w", encoding="utf-8") as t_file:
                t_file.write(MOCK_TEMPLATE)
            #
            with patch.dict(
                os.environ,
                {
                    "CI_PROJECT_TITLE": mock_project_title,
                    "CI_PROJECT_URL": mock_project_url,
                },
            ):
                result = ExecResult.from_call(
                    "-f",
                    template_file_name,
                    "-o",
                    tempdir,
                    stdout=mock_stdout,
                )
                with self.subTest("returncode"):
                    self.assertEqual(result.returncode, RETURNCODE_OK)
                #
            #
            output_file_name = f"{tempdir}/example.md"
            with open(output_file_name, "r", encoding="utf-8") as o_file:
                output = o_file.read().strip()
            #
            with self.subTest("result"):
                self.assertEqual(
                    output,
                    "# Build information\n\n"
                    "_provided by [glsr-present]"
                    "(https://pypi.org/project/glsr-present/)\n"
                    f"{commandline.__version__}"
                    " WITH A USER-SUPPLIED TEMPLATE_\n\n"
                    f"[{mock_project_title}]({mock_project_url})",
                )
            #
        #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
