#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Package commands interface"""

import functools

from imagepills import entrypoint, pills

# Entry points defintionng
size = functools.partial(entrypoint.size, pills.Size)
image2png = functools.partial(entrypoint.image2png, pills.Convert2PNG)
resize = functools.partial(entrypoint.resize, pills.Resize)
