#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the GPLv3 license, a copy of
# which is included in the root directory of this package.
#
import logging
import numpy as np
from maptools.util import read, write, read_axis_order
from maptools._reorder import reorder


# Get the logger
logger = logging.getLogger(__name__)


def accumulate(
    input_map_filename: list,
    output_map_filename: str,
):
    """
    Accumulate the maps

    """

    # Initialise data to None
    data = None
    reference_file = None

    # Open the input files
    for filename in input_map_filename:
        print("Reading %s" % filename)
        infile = read(filename)
        if data is None:
            data = infile.data.copy()
            reference_file = infile
        else:
            data += reorder(
                infile.data, read_axis_order(infile), read_axis_order(reference_file)
            )

    # Write the output file
    if data is not None:
        outfile = write(output_map_filename, np.array(data), infile=reference_file)
