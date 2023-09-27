# -*- coding: utf-8 -*-

"""

glsr_present.__main__

python3 -m glsr_present command line script

Copyright (C) 2023 Rainer Schwarzbach

This file is part of glsr-present.

glsr-present is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

glsr-present is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import sys

from typing import List, Optional

from glsr_present import commandline


#
# Functions
#


def main(args: Optional[List[str]] = None) -> int:
    """Use the query parser to construct
    an access.Path subclass instance from the original query.
    Then, execute the program using that instance together with
    the provided command line arguments.

    :param args: the list of command line arguments,
        or None to go with the default (sys.argv).
    :returns: the script returncode
    """
    program = commandline.Program(args)
    return program.execute()


if __name__ == "__main__":
    sys.exit(main())  # NOT TESTABLE


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
