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
import tempfile

from unittest import TestCase

from unittest.mock import patch

from glsr_present import commandline
from glsr_present import __version__

from .commons import GenericCallResult, RETURNCODE_OK


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
    def test_dummy(self, mock_stdout):
        """Dummy Test"""
        with tempfile.TemporaryDirectory() as tempdir:
            result = ExecResult.from_call(
                "-o",
                tempdir,
                stdout=mock_stdout,
            )
        #
        self.assertEqual(result.returncode, RETURNCODE_OK)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_version(self, mock_stdout):
        """version output test"""
        with self.assertRaises(SystemExit) as cmgr:
            commandline.Program(["--version"]).execute()
        #
        self.assertEqual(cmgr.exception.code, RETURNCODE_OK)
        self.assertEqual(mock_stdout.getvalue().strip(), __version__)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
