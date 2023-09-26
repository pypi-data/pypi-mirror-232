#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Base file"""

import argparse


class Arguments:  # pragma: no cover
    """Class to extract command line args"""

    def __init__(self, pill_name) -> None:
        """Default constructor"""

        # parser initialization
        self.parser = argparse.ArgumentParser(pill_name)

        # This variable contains the command line arguments passed
        self.args = None

        # Initialize default args
        self._set_default_args()

    def _set_default_args(self):
        """Method that create default arguments"""
        self.parser.add_argument(
            "-v",
            "--verbose",
            help="Set verbose option",
            dest="verbose",
            required=False,
            action="store_true",
        )

    def add_argument(self, *arg, **kwargs):
        """Method to add new item to the parser

        :param **arg: new argument definition
        """
        self.parser.add_argument(*arg, **kwargs)

    def parse_arguments(self):
        """Method for parsing arguments"""
        self.args = self.parser.parse_args()

    def show_help(self):
        """Method fro printing help"""
        self.parser.print_help()


class Pill(Arguments):  # pragma: no cover
    """Base class for pills

    This class inherits from the Arguments class in order to handle
    command line arguments.

    Inheritance class from Pill should call super with command string name as follows:

    ```python
    super().__init__(command_name)
    ```

    From the Arguments class, verbose command is implemented by default, as well as the
    help option to show the arguments information.

    We can add more arguments by calling the method add_argument from the Arguments class
    as follows:

    ```python
    self.add_argument(*arg, **kwargs)
    ```

    The **arg** parameter takes care about a list of variable arguments.
    The **kwargs** parameter handles a dictionary (key value paired) of a list of variable
    arguments.
    """

    def run(self):
        """This method handles the execution of the pill.

        This method has to be overriden for each pill.
        """

        # TODO: This method should read the command line arguments as follows:
        # args = self.parser.parse_args()

        # TODO: Then, we should implement the pill action code.
