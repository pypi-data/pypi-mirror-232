# -*- coding: utf-8 -*-

"""

glsr_present.commandline

Command line functionality

Copyright (C) 2023 Rainer Schwarzbach

This file is part of glsr-present.

glsr-present is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

glsr-present is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import argparse
import logging
import os
import pathlib
import shutil

# import sys

from typing import List, Optional

from jinja2 import Environment, PackageLoader, select_autoescape

# from glsr_present import commons
from glsr_present import __version__


#
# Constants
#


RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


#
# classes
#


class Program:

    """Command line program"""

    name: str = "glsr_present"
    description: str = "GitLab Security Reports - Presenter"

    def __init__(self, args: Optional[List[str]] = None) -> None:
        """Parse command line arguments and initialize the logger

        :param args: a list of command line arguments
        """
        self.__arguments = self._parse_args(args)
        if self.__arguments.loglevel < logging.INFO:
            message_format = (
                "%(levelname)-8s | (%(funcName)s:%(lineno)s) %(message)s"
            )
        else:
            message_format = "%(levelname)-8s | %(message)s"
        #
        logging.basicConfig(
            format=message_format,
            level=self.__arguments.loglevel,
        )

    @property
    def arguments(self) -> argparse.Namespace:
        """Property: command line arguments

        :returns: the parsed command line arguments
        """
        return self.__arguments

    def _parse_args(self, args: Optional[List[str]]) -> argparse.Namespace:
        """Parse command line arguments using argparse
        and return the arguments namespace.

        :param args: a list of command line arguments,
            or None to parse sys.argv
        :returns: the parsed command line arguments as returned
            by argparse.ArgumentParser().parse_args()
        """
        main_parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
        )
        main_parser.set_defaults(
            loglevel=logging.WARNING,
            output_directory=pathlib.Path("docs"),
            template="build-info.md.j2",
        )
        main_parser.add_argument(
            "--version",
            action="version",
            version=__version__,
            help="print version and exit",
        )
        logging_group = main_parser.add_argument_group(
            "Logging options", "control log level (default is WARNING)"
        )
        verbosity = logging_group.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-d",
            "--debug",
            action="store_const",
            const=logging.DEBUG,
            dest="loglevel",
            help="output all messages (log level DEBUG)",
        )
        verbosity.add_argument(
            "-v",
            "--verbose",
            action="store_const",
            const=logging.INFO,
            dest="loglevel",
            help="be more verbose (log level INFO)",
        )
        verbosity.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=logging.ERROR,
            dest="loglevel",
            help="be more quiet (log level ERROR)",
        )
        main_parser.add_argument(
            "-o",
            "--output-directory",
            type=pathlib.Path,
            help="output directory(default: %(default)s)",
        )
        main_parser.add_argument(
            "-t",
            "--template",
            help="template for the overview page (default: %(default)s)",
        )
        return main_parser.parse_args(args)

    # pylint: disable=too-many-locals
    def execute(self) -> int:
        """Execute the program
        :returns: the returncode for the script
        """
        returncode = RETURNCODE_OK
        base_path = pathlib.Path(__file__).parent.resolve()
        source_path = base_path / "static"
        for source_file in source_path.glob("*"):
            shutil.copy2(
                source_file, self.arguments.output_directory / source_file.name
            )
        #
        found_reports = []
        report_source_path = pathlib.Path(os.getcwd()).resolve()
        for source_file in report_source_path.glob("gl-*-report.json"):
            shutil.copy2(
                source_file, self.arguments.output_directory / source_file.name
            )
            found_reports.append(source_file.name)
        #
        env = Environment(
            loader=PackageLoader("glsr_present"),
            autoescape=select_autoescape(),
        )
        j2_template = env.get_template(self.arguments.template)
        data = []
        for report_file_name in found_reports:
            middle = report_file_name[3:-12]
            if middle in (
                "iac-sast",
                "container-scanning",
                "secret-detection",
            ):
                report_type = middle
            else:
                report_type = "sast"
            #
            data.append((report_type, report_file_name))
        #
        output_path = (
            self.arguments.output_directory / self.arguments.template[:-3]
        )
        with open(output_path, "w", encoding="utf-8") as link_file:
            link_file.write(j2_template.render(reports=data))
        #
        logging.warning("Files in %s:", self.arguments.output_directory)
        for file_path in self.arguments.output_directory.glob("*"):
            logging.warning(" - %s", file_path)
        #
        return returncode


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
