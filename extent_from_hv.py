#/home/bdavis/Projects/lcmap/pyccd-cmd-line/.venv/bin/python

########################################################################
#
# extent_from_hv
#
# This function was taken from a main() developed by klsmith, and
# converted to a callable so other mains, functions, methods, notebooks,
# etc., can use it.
#
########################################################################

from collections import namedtuple
from pprint import pprint


########################################################################
#
# Set up the data structures.
#
########################################################################

GeoExtent = namedtuple('GeoExtent', ['x_min', 'y_max', 'x_max', 'y_min'])
GeoAffine = namedtuple('GeoAffine', ['ul_x', 'x_res', 'rot_1', 'ul_y', 'rot_2', 'y_res'])


########################################################################
#
# These are the values, in northing and easting, in meters, for Albers
# Conical Equal Area for CONUS.  Probably should not be hard-coded.
# However, we are currently location and projection limited.
#
########################################################################

CONUS_EXTENT = GeoExtent(x_min=-2565585,
                         y_min=14805,
                         x_max=2384415,
                         y_max=3314805)


def extent_from_hv(h, v, loc):

    loc = loc.lower()


    ####################################################################
    #
    # Calculate the upper left to lower right extents, based on
    # 5,000 x 5,000 pixel ARD tile sizes, and 30m Landsat resolution.
    #
    ####################################################################

    if loc == 'conus':
        xmin = CONUS_EXTENT.x_min + h * 5000 * 30
        xmax = CONUS_EXTENT.x_min + h * 5000 * 30 + 5000 * 30
        ymax = CONUS_EXTENT.y_max - v * 5000 * 30
        ymin = CONUS_EXTENT.y_max - v * 5000 * 30 - 5000 * 30
    else:
        raise Exception('Location not implemented: {0}'
                        .format(loc))

    ####################################################################
    #
    # Define and return the values for the specific h and v passed in,
    # along with the tile name for that location.
    #
    ####################################################################

    tile = 'H' + str(h).zfill(2) + 'V' + str(v).zfill(2)
    
    return (tile, xmin, ymax)
