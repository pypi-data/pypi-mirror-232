#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""File that contains image tools"""

import os
import sys

from PIL import Image, UnidentifiedImageError

from imagepills import base, utils

__author__ = "Marco Espinosa"
__email__ = "marco@marcoespinosa.es"
__date__ = "16/06/2023"
__version__ = "1.0"
__type__ = "module"


class Size(base.Pill):
    """Class to handle image size calls"""

    def __init__(self, name) -> None:
        """Deafult constructor"""

        # Initialize base class
        super().__init__(name)

        # Configure specific command line arguments
        self._configure_args()

        # Parse args. This function provides the parsed args in the self.args variable
        self.parse_arguments()

        # Initialization of list of images and sizes.
        # Format: list of dictionary: {'filename', 'weight', 'height'}
        self.output = []

    def __repr__(self) -> str:
        return "Size class"

    def _configure_args(self):  # pragma: no cover
        """Method for adding command lines to the base class"""

        # Argument to provide an input folder path for recursively showing their sizes.
        self.add_argument(
            "-i",
            "--input_folder",
            help="Path to images folder",
            dest="input_folder",
            metavar="STRING",
            required=False,
        )

        # Argument to provide an input file for showing its size.
        self.add_argument(
            "-f",
            "--file",
            help="file path",
            dest="input_file",
            metavar="STRING",
            required=False,
        )

    def run(self):
        """Run method"""

        if not self.args.input_folder and not self.args.input_file:
            self.show_help()
            sys.exit(99)

        filenames = []

        if self.args.input_folder:
            filenames = utils.walk(self.args.input_folder)
        elif self.args.input_file:
            filenames.append(self.args.input_file)

        for filename in sorted(filenames):
            try:
                img = None
                if self.args.input_folder:
                    img = Image.open(os.path.join(self.args.input_folder, filename))
                else:
                    img = Image.open(filename)

                if img and self.args.verbose:
                    self.output.append(
                        {
                            "filename": os.path.basename(filename),
                            "width": img.width,
                            "height": img.height,
                        }
                    )

            except (TypeError, UnidentifiedImageError):
                if filename:
                    print(
                        f"{filename}: An exception occured when opening the image! Cannot identify image file."
                    )

        # Print output
        if self.output:
            print(self.output)


class Convert2PNG(base.Pill):
    """Class to handle image convertion to PNG"""

    def __init__(self, name) -> None:
        """Deafult constructor"""

        # Initialize base class
        super().__init__(name)

        # Configure specific command line arguments
        self._configure_args()

        # Parse args. This function provides the parsed args in the self.args variable
        self.parse_arguments()

    def __repr__(self) -> str:
        return "Convert2PNG class"

    def _configure_args(self):  # pragma: no cover
        """Method for adding command lines to the base class"""

        # Argument to provide an input folder path for recursively get the images.
        self.add_argument(
            "-i",
            "--input_folder",
            help="Path to images folder",
            dest="input_folder",
            metavar="STRING",
            required=False,
        )

        # Argument to provide an output folder for converted files.
        self.add_argument(
            "-o",
            "--output_folder",
            help="Path to ouput folder",
            dest="output_folder",
            metavar="STRING",
            required=True,
            type=utils.normalize_folder,
        )

        # Argument to provide an input file to convert.
        self.add_argument(
            "-f",
            "--file",
            help="file to convert",
            dest="input_file",
            metavar="STRING",
            required=False,
        )

    def run(self):
        """Run method"""

        # Ouput initialization
        successes = []
        errors = []

        if self.args.input_folder:
            filenames = utils.walk(self.args.input_folder)

            for filename in sorted(filenames):
                success, error = self.save_to_png(
                    os.path.join(self.args.input_folder, filename),
                    filename,
                    self.args.output_folder,
                )
                # Save output:
                if success:
                    successes.append(success)
                if error:
                    errors.append(error)

        elif self.args.input_file:
            success, error = self.save_to_png(
                self.args.input_file, self.args.input_file, self.args.output_folder
            )
            # Save output:
            if success:
                successes.append(success)
            if error:
                errors.append(error)

        if self.args.verbose:
            output = [{"success": successes, "errors": errors}]
            print(f"{output}")

    def save_to_png(self, input_file, filename, folder=None):
        """Save image in png format"""
        # Initialize values for return tuple
        success = None
        error = None

        try:
            img = Image.open(input_file)

            if folder:
                img.save(
                    os.path.join(
                        folder, f"{os.path.basename(filename).split('.')[0]}.png"
                    )
                )
            else:
                img.save(f"{filename.split('.')[0]}.png")

            success = filename

        except (TypeError, UnidentifiedImageError):
            if filename:
                print(
                    f"{filename}: An exception occured when opening the image! Cannot identify image file."
                )

                error = filename

        return success, error


class Resize(base.Pill):
    """Class to handle image resizing"""

    def __init__(self, name) -> None:
        """Deafult constructor"""

        # Initialize base class
        super().__init__(name)

        # Configure specific command line arguments
        self._configure_args()

        # Parse args. This function provides the parsed args in the self.args variable
        self.parse_arguments()

    def __repr__(self) -> str:
        return "Resize class"

    def _configure_args(self):  # pragma: no cover
        """Method for adding command lines to the base class"""

        # Argument to provide an output folder for converted files.
        self.add_argument(
            "-o",
            "--output_folder",
            help="Path to ouput folder",
            dest="output_folder",
            metavar="STRING",
            required=True,
            type=utils.normalize_folder,
        )

        # Argument to provide an input file to convert.
        self.add_argument(
            "-f",
            "--file",
            help="file to convert",
            dest="input_file",
            metavar="STRING",
            required=True,
        )

        # Argument to provide width.
        self.add_argument(
            "-w",
            "--width",
            help="new width",
            dest="width",
            metavar="STRING",
            required=True,
            type=utils.check_minimum_size,
        )

        # Argument to provide height.
        self.add_argument(
            "-e",
            "--height",
            help="new height",
            dest="height",
            metavar="STRING",
            required=True,
            type=utils.check_minimum_size,
        )

    def run(self):
        """Run method"""

        # ! New width and heigh will be proportional
        # Ouput initialization
        successes = []
        errors = []

        # Open image
        img = Image.open(self.args.input_file)

        # Get new sizes
        new_width = self.args.width
        new_height = self.args.height

        # Check which is the highest size and calculate the other proportionally
        if self.args.width >= self.args.height:
            wpercent = new_width / float(img.size[0])
            new_height = int(float(img.size[1]) * float(wpercent))
        else:
            wpercent = new_height / float(img.size[1])
            new_width = int(float(img.size[0]) * float(wpercent))

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        img.save(
            os.path.join(
                self.args.output_folder,
                f"{os.path.basename(self.args.input_file).split('.')[0]}_{new_width}x{new_height}.png",
            )
        )

        successes.append(
            os.path.join(
                self.args.output_folder,
                f"{os.path.basename(self.args.input_file).split('.')[0]}_{new_width}x{new_height}.png",
            )
        )

        if self.args.verbose:
            output = [{"success": successes, "errors": errors}]
            print(f"{output}")
