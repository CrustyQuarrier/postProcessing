#!/home/bdavis/Projects/lcmap/pyccd-cmd-line/.venv/bin/python

########################################################################
#
# count_json_results.py
#
# bdavis
#
# 20170901
#
# Args:
#     directory location containing .json file(s)
#
# After downloading .json files from cassandra, but before using them
# to produce visual change products (.tif), we previously did a file
# size check, to indicate there were results (or not).  We need to
# interject better quality assurance at this step, and verify there are
# 10,000 x/y locations with successful pyccd processing status.  There
# may be no coefficients, or no models run, but completion of processing
# and successful EOJ status will allow all 10,000 X/Y locatioins to be
# processed successfully by subsequent steps.
#
# To do this, we must check the tag result_ok for true.  Other values,
# or missing status, or no status/results/entry of any kind should me
# identified for investigation, and this .json set prevented from
# passing on the the next processing step.
#
########################################################################

import os
import sys
import time
import datetime
import multiprocessing as mp
import numpy as np
from pprint import pprint

import json


########################################################################
#
# make_points defines the x and y values to expect in a tile.
#
########################################################################

def make_points(type, start_x, start_y):

    if (type == 'tile'):

        ################################################################
        # chips within a tile
        ################################################################

        xr = range(start_x, start_x+(30*5000),  (30*100))
        yr = range(start_y, start_y-(30*5000), -(30*100))

    elif (type == 'chip'):

        ################################################################
        # points within a chip
        ################################################################
        xr = range(start_x, start_x+(30*100),  (30))
        yr = range(start_y, start_y-(30*100), -(30))

    return [(x,y) for y in yr for x in xr]


def get_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        return None


def load_jsondata(jdata, tile, x, y, num_valid_chips):

    num_true, num_untrue = 0, 0

    if jdata is not None:

        json_total_points = []
        json_total_points = make_points('chip', int(x), int(y))

        json_ok_points = []
        json_untrue_points = []

        for j in jdata:
            
            col = int((j['x'] - j['chip_x']) / 30)
            row = int((j['chip_y'] - j['y']) / 30)

            # old style
            if j.get('result_ok') is True:
            # firebird
            #if j.get('error' == 'None'):

                ########################################################
                # add this x/y (col/row) to the list of good points
                # in the chip list, to compare against the total
                # list of 10,000 points. (slice operation?)
                ########################################################

                json_ok_points.append((j['x'], j['y']))
                num_true += 1

            else:

                ########################################################
                # add to the list of bad points
                ########################################################

                json_untrue_points.append((j['x'], j['y']))
                num_untrue +=1

    ####################################################################
    # only report the x/y points with bad status or missing from the
    # .json file. A good chip is not reported.  Output can be redirected
    # to a inventory text file.
    ####################################################################

    if (num_untrue != 0):

        chip = tile+'_'+x+'_'+y
        print ("Chip: ", chip, "Number of Points result_ok NOT true: ", num_untrue)
        print ("    point x/y's: ", json_untrue_points)
        print ("")

    elif (num_true != 10000):

        chip = tile+'_'+x+'_'+y
        expected = set(json_total_points)
        actual = set(json_ok_points)
        print ("Chip: ", chip, "Number of Points missing: ", len(expected.difference(actual)))
        print ("    point x/y's: ", expected.difference(actual))
        print ("")

    else:

        num_valid_chips += 1

    return num_valid_chips


if len(sys.argv) == 2:
    path = sys.argv[1]
else:
    print ('Invalid number of args: ', len(sys.argv))
    print ('Usage: python count_json_results.py <path-to-.json-files>')
    exit()

print (datetime.datetime.now())
print ("")

json_file_list =  [j for j in os.listdir(path) if j.endswith('.json')]

os.chdir(path)

num_valid_chips = 0

for j in json_file_list:

    # old style
    tile, x, y = j.split('_', 3)
    y, ext = y.split('.', 2)
    # firebird
    #alg, yr, mo, da, x, y = j.split('_', 6)
    #y, ext = y.split('.', 2)

    num_valid_chips = load_jsondata(get_json(j), tile, x, y, num_valid_chips)

print ("Number of Valid Chips for tile ", tile, ":", num_valid_chips)
print ("")
print (datetime.datetime.now())
