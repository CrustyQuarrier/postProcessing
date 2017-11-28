#!/home/bdavis/Projects/lcmap/pyccd-cmd-line/.venv/bin/python

########################################################################
#
# compare_json_results.py
#
# bdavis
#
# 20171130
#
# Args:
#     Two .json file(s) for the same chip from two different pyccd
#     versions
#     Tolerence value.  For numerical contents, such as coeeficients,
#     define a tolerance for architectural differences.  Something
#     small like 0.0001.  There are a limited number of significant
#     digits to compare.  Very large absolute values consume more
#     digits to the left of the decimal, leaving fewer to the right
#     to incorporate into tolerance value comparisons.
#
# To ensure there are no unitended conswquences from updating the PyCCD
# software, an automated method for comparing the results contained in
# .json chip files from 2 different results is required.  All 10,000
# X-Y locations will be compared, and any disrepencies printed to stdout
# to identify issues for further investigation.
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


########################################################################
#
# get_json opens the .json disk file, and returns the loaded data.
#
########################################################################

def get_json(json_file):

    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            return json.load(f)
    else:
        return None


########################################################################
#
# load_jsondata loads contents of each of the 2 input files into 
# individual objects, and loops through all of them, while comparing
# values.
#
########################################################################

def load_jsondata(jdata1, jdata2, tol_val, num_valid_locations):

    num_true, num_untrue = 0, 0

    if (jdata1 is not None) and (jdata2 is not None):

        ################################################################
        #
        # x-y locations are not stored in any sequential order, results
        # are written as they complete.  They cannot be assumed to exist
        # in a pixel-by-pixel, row-major order, or any other order.
        # Therefore, just read the results and store in dicts that of
        # the correct size & shape, and index the entries with the x
        # and y values for each.
        #
        # Then they can be compared sequentially in nested for loops.
        # Or something more elegant.....
        #
        # Not so fast, blunder-butt.  It appears they may me retrieved
        # in an organized manner from Cassandra.  Lets give it a try
        # first.
        #
        ################################################################

        index = 0
        for j1 in jdata1:

            first_xy_err_flag = True
            err_count = 0
            coeff_err_count = 0
            j2 = jdata2[index]

            result_stat1 = j1.get('result_ok')
            result_stat2 = j2.get('error')


            ############################################################
            #
            # put entire result(s) into a dict
            #
            ############################################################

            result1 = json.loads(j1.get('result', 'null'))
            result2 = json.loads(j2.get('result', 'null'))


            ############################################################
            #
            # log algorithm versions
            #
            ############################################################

            if index == 0:
                print ('Algorithms: ', result1['algorithm'], ',', (result2['algorithm']))


            ############################################################
            #
            # Check status of result.  Calling this a fatal error,
            # becuse results should at least be complete, if not
            # matching.  After this, shen things do not match, log the
            # difference, but keep going, to get all the diffs to
            # investigate.  Hopefully they are few.  If not, just
            # adjust tolerance value downward and run again.
            #
            ############################################################

            if result_stat1 != True or result_stat2 != 'null':
                print ('bad results status')
                print (j1.get('result_ok'))
                print (j2.get('error'))
                print ('result_stat1:', result_stat1, 'result_stat2:', result_stat2)
                err_count += 1
                return -1
            else:
                pass

            chip_x1 = int(j1['chip_x'])
            chip_y1 = int(j1['chip_y'])

            chip_x2 = int(j2['chip_x'])
            chip_y2 = int(j2['chip_y'])


            ############################################################
            #
            # Ensure x and y match
            #
            ############################################################

            if chip_x1 != chip_x2 and chip_y1 != chip_y2:
                print ('chip x and chip y are not the same')
                err_count += 1
                #return -1

            x1 = int(j1['x'])
            y1 = int(j1['y'])

            x2 = int(j2['x'])
            y2 = int(j2['y'])

            if x1 != x2 and y1 != y2:
                print ('x and y are not the same')
                err_count +=1
                #return -1
            else:
                pass


            ############################################################
            #
            # Compare number of models
            #
            ############################################################

            num_mod1 = len(result1['change_models'])
            num_mod2 = len(result2['change_models'])
            if (num_mod1 != num_mod2):
                if first_xy_err_flag:
                    print ('Comparing x', x1, 'y', y1)
                print ('Number of Change Models are not the same', num_mod1, 'vs.', num_mod2)
                first_xy_err_flag = False
                err_count +=1
            

            ############################################################
            #
            # Loop through all change models in each result
            #
            ############################################################

            for mod_num in range(0, num_mod1):

                obs_count1 = result1['change_models'][mod_num]['observation_count']
                obs_count2 = result2['change_models'][mod_num]['observation_count']
                start_day1 = result1['change_models'][mod_num]['start_day']
                start_day2 = result2['change_models'][mod_num]['start_day']
                end_day1 = result1['change_models'][mod_num]['end_day']
                end_day2 = result2['change_models'][mod_num]['end_day']
                break_day1 = result1['change_models'][mod_num]['break_day']
                break_day2 = result2['change_models'][mod_num]['break_day']
                if (obs_count1 != obs_count2 and
                    start_day1 != start_day2 and
                    end_day1   != end_day2   and
                    break_day1 != break_day2):

                    if first_xy_err_flag:
                        print ('Comparing x', x1, 'y', y1)
                        first_xy_err_flag = False
                    print ('day(s) for change model', mod_num, 'are not the same')
                    print ('obersvation_count:', obs_count1, obs_count2)
                    print ('start_day:', start_day1, start_day2)
                    print ('end_day:', end_day1, end_day2)
                    print ('break_day:', break_day1, break_day2)
                    err_count +=1
                    #return -1
                else:
                    pass
                    #print ('days match')

                curve_qa1 = result1['change_models'][mod_num]['curve_qa'] 
                curve_qa2 = result2['change_models'][mod_num]['curve_qa'] 
                if (curve_qa1 != curve_qa2):
                    if first_xy_err_flag:
                        print ('Comparing x', x1, 'y', y1)
                    print ('curve_qa for model', mod_num, 'NOT the same', curve_qa1, 'vs.', curve_qa2)
                    first_xy_err_flag = False
                    err_count +=1

                ########################################################
                #
                # Loop through all numeric values in all bands
                #
                ########################################################

                for band in ('swir1', 'blue', 'red', 'thermal', 'swir2', 'nir', 'green'):
                    c1_1, c2_1, c3_1, c4_1, c5_1, c6_1, c7_1= result1['change_models'][mod_num][band]['coefficients']
                    c1_2, c2_2, c3_2, c4_2, c5_2, c6_2, c7_2= result2['change_models'][mod_num][band]['coefficients']
                    intercept1 = result1['change_models'][mod_num][band]['intercept']
                    rmse1      = result1['change_models'][mod_num][band]['rmse']
                    magnitude1 = result1['change_models'][mod_num][band]['magnitude']
                    intercept2 = result2['change_models'][mod_num][band]['intercept']
                    rmse2      = result2['change_models'][mod_num][band]['rmse']
                    magnitude2 = result2['change_models'][mod_num][band]['magnitude']

                    ####################################################
                    #
                    # Try to do all dicts at once, for only 1 code set
                    # of checks and prints.
                    #
                    ####################################################

                    for val1, val2, element in zip((c1_1,c2_1,c3_1,c4_1,c5_1,c6_1,c7_1,intercept1,rmse1,magnitude1),
                                                   (c1_2,c2_2,c3_2,c4_2,c5_2,c6_2,c7_2,intercept2,rmse2,magnitude2),
                                                   ('coeffs1', 'coeffs2', 'coeffs3', 'coeffs4', 'coeffs5',
                                                    'coeffs6', 'coeffs7', 'intercepts', 'rmses', 'magnitudes')):

                        if (val2 - tol_val) <= val1 <= (val2 + tol_val):
                            pass
                        else:
                           err_count +=1
                           if first_xy_err_flag == True:
                               print ('Comparing x', x1, 'y', y1)
                               first_xy_err_flag = False
                           print ('  ', band, element, 'for model', mod_num, 'NOT within tolerance')
                           print ('    result 1:', val1)
                           print ('    result 2:', val2)
                           print ('')

            if err_count == 0:
                num_valid_locations += 1

            index += 1

        json_total_points = []
        json_total_points = make_points('chip', x1, y1)

        json_ok_points = []
        json_untrue_points = []

    return num_valid_locations


########################################################################
#
# Check args, regurtitate if correct number, else spit out a usage
# message and exit.
#
########################################################################

if len(sys.argv) == 4:
    json1 = sys.argv[1]
    json2 = sys.argv[2]
    tolerance_value = float(sys.argv[3])
    print ('')
    print ('json1:     ', json1)
    print ('json2:     ', json2)
    print ('tolerance: ', tolerance_value)
    print ('')
else:
    print ('')
    print ('Invalid number of args: ', len(sys.argv))
    print ('Usage: python compare_json_results.py <first-.json-file> <second-.json-file> <tolerance_value>')
    print ('Example: python compare_json_results.py H19V14_284415_1214805_v1.json H19V14_284415_1214805_v2.json 0.000001')
    print ('')
    exit()

print (datetime.datetime.now())
print ('')

num_valid_locations = 0

jdata1 = get_json(json1)
jdata2 = get_json(json2)

num_valid_locations = load_jsondata(jdata1, jdata2, tolerance_value, num_valid_locations)

print ('')
print ('Number of Valid X-Y Locations: ', num_valid_locations)
print ('')
print (datetime.datetime.now())
