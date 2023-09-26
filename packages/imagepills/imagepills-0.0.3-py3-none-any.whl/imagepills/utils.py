#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utils library module"""
import argparse
import os


def walk(root) -> list:
    """Method to walk throught the given folder

    :param root: root folder

    :return: list of files
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # yield every filename to updload
        for filename in filenames:
            # print(os.path.join(dirpath, filename))
            files.append(filename)
        # call the method recursively for the subfolders
        for dirname in dirnames:
            walk(os.path.join(dirpath, dirname))

    return files


def normalize_folder(folder) -> str:
    """Method that normalizes the folder

        Normalization:
            - Strip right / or \\
            - if a . is provided, it converts to the current path

        :param folder: string that contains a folder path.

        :return: normalized folder
    """
    _folder = folder.rstrip("\\/")

    return _folder if _folder != "." else os.path.split(os.path.abspath(__file__))[0]


def check_minimum_size(value) -> int:
    """Method to check if the size provided is integer and at least 256

    :param value: int size. Height or width should be passed as argument.

    :return: int value or raise argsparse.ArgumentTypeError execption
    """

    try:
        int_val = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("The value must be an integer number") from exc

    if int_val < 256:
        raise argparse.ArgumentTypeError("The value must be at least 256px")

    return int_val
