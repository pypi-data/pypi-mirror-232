#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Entry point commands interface"""


def entry_point_factory(entry_point_name):
    """Entry point with name"""

    def entrypoint(command):
        """Entry point method for lsimagesize command"""
        # print(command)
        command_class = command(entry_point_name)
        command_class.run()

    return entrypoint


size = entry_point_factory("size")
image2png = entry_point_factory("image2png")
resize = entry_point_factory("resize")
