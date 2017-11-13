#!/home/bdavis/Projects/lcmap/pyccd-cmd-line/.venv/bin/python

########################################################################
# 
# Overview
# 
# This script is taken from PyCCD Results notebook used to:
# 
#     Check on progress of pyccd results for a tile
#     Optionally download them
#     Optionally request the be created
#
# env set up before invoking script:
#
# pip freeze:
#    cassandra-driver==3.10
#    numpy==1.13.1
#    PyYAML==3.12
#    requests==2.14.2
#    scikit-learn==0.19.0
#    scipy==0.19.1
#    six==1.11.0
#
# Depends on:
#    extent_from_hv.py
#
# Retrieving Data
#
# You can retrieve results from the Clownfish REST API or you can access
# Cassandra directly. Direct access to Cassandra avoids the overhead of
# HTTP. In general, this is not a good idea, but we know what we're
# doing... ;-) ...so it's ok.
#
########################################################################

import os
import sys

import requests

from cassandra.cluster import Cluster, ExecutionProfile
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import ordered_dict_factory
from cassandra import ConsistencyLevel

from multiprocessing.dummy import Pool as ThreadPool 

from extent_from_hv import extent_from_hv

import json
from datetime import datetime


########################################################################
#
# This function creates a session, used to execute CQL.
#
########################################################################

def setup_session(username, password, hosts, keyspace):

    print ('')
    print ('Setting Up Session Profile ...')
    
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(hosts, auth_provider=auth_provider)
    
    session = cluster.connect(keyspace)
    session.row_factory = ordered_dict_factory
    
    print ('Session Created ..............')
    
    return session

########################################################################
#
# Request execution using the defined set of points.
#
########################################################################

def request_execution(algorithm, x, y, refresh):

    URL = 'http://lcmap-test.cr.usgs.gov/v1/changes/results/{algorithm}/{x}/{y}?refresh={refresh}'
    url = URL.format(algorithm=algorithm, x=x, y=y, refresh=refresh)
    return requests.get(url).json()


########################################################################
#
# Chip Points in a Tile-stack
# 
# In order to count or retrieve or request change results, you will need
# to create a list of x-y points to work with.  The following function
# generates a row-major list of points that can be used to request,
# retrieve, or produce JSON files.
#
########################################################################

def make_points(start_x, start_y):
    xr = range(start_x, start_x+(30*5000),  (30*100))
    yr = range(start_y, start_y-(30*5000), -(30*100))
    return [(x,y) for y in yr for x in xr]


########################################################################
#
# This function is used to count results for a chip. Useful for
# determining where algorithm execution failed to complete.
#
########################################################################

def count_results(x, y, algorithm, session, status_result):

    result = session.execute(status_result, (x, y, algorithm))
    return (x,y,algorithm,result[0]['count'])


########################################################################
#
# Prepare the session to use.  Useful to separate this out so different
# session specs can be isolated.
#
########################################################################

def status_result():
    print ('Preparing Session ........')
    session.prepare("SELECT count(result_ok) as count FROM results WHERE chip_x=? AND chip_y=? AND algorithm=?")


########################################################################
#
# Check for validity of serial-izing the object.
#
########################################################################

def json_serial(obj):

    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


########################################################################
#
# Extractig pyccd results to local filesystem .json format files, for
# subsequent production of visual change products (change map tifs).
#
########################################################################


def save_chip(path_template, site, tile, x, y, algorithm):

    ####################################################################
    #
    # I have no idea why I have to do this again here, but if I do not,
    # I get a session error.......
    # ToDo: Fix later.
    #
    ####################################################################

    username=os.environ["LCMAP_USERNAME"]
    password=os.environ["LCMAP_PASSWORD"]
    hosts=[os.environ["LCMAP_HOSTS"]]
    keyspace=os.environ["LCMAP_KEYSPACE"]
    session = setup_session(username, password, hosts, keyspace)

    entire_result = session.prepare("SELECT * FROM results WHERE chip_x=? AND chip_y=? AND algorithm=?")

    result = session.execute(entire_result, (x, y, algorithm))

    ####################################################################
    #
    # Create the full directory-file name to write.   Then write it.
    #
    ####################################################################

    version_base, version_num = algorithm.split(':', 1)
    path = path_template.format(site=site, tile=tile, x=x, y=y, version_num=version_num)

    print ('Saving .json ........')

    with open(path,'w') as outfile:
        json.dump(list(result), outfile, default=json_serial)
    return path


########################################################################
#
# Start of main definition.
#
########################################################################

def main(site, h, v, algorithm, option):

    ####################################################################
    #
    # Determine the upper-left coordinates for the ARD tile specified.
    # Create the list of x/y values in a list.
    #
    ####################################################################

    tile, x, y = extent_from_hv(h, v, 'conus')

    points = make_points(x, y)

    refresh = True


    ####################################################################
    #
    # Now you can request execution using that set of points.
    # You will need credentials.  However, numeric ip addresses and 
    # passwords, etc., should not be made public, on a git repository,
    # for example.  Therefore, retrieve from the user environment.
    #
    ####################################################################

    username=os.environ["LCMAP_USERNAME"]
    password=os.environ["LCMAP_PASSWORD"]
    hosts=[os.environ["LCMAP_HOSTS"]]
    keyspace=os.environ["LCMAP_KEYSPACE"]

    session = setup_session(username, password, hosts, keyspace)

    status_result = session.prepare("SELECT count(result_ok) as count FROM results WHERE chip_x=? AND chip_y=? AND algorithm=?")

    status_result.consistency_level = ConsistencyLevel.QUORUM
    #if option in ('count', 'request', 'retrieve'):
    if option in ('count', 'request'):

        ####################################################################
        #
        # Counting Results
        # You may find it useful to count the number of results produced for
        # a specific chip. You can do this in parallel...
        # Below are some more utility functions for counting results.
        #
        ####################################################################

        print ('Counting tile: ', tile, 'x: ', x, 'y: ', '.....................')


        ####################################################################
        #
        # Checking for consistency error.
        #
        # Then, be cautious using too many threads when the system is loaded
        # with other work.  Using more than 4 when the system is idle adds
        # little benefit.  Otherwise, 2 is probably low-impact.  Remember,
        # all the nodes must be polled, so there will be some impact to 
        # other processes reading from and writing to the DB.
        #
        ####################################################################

        ##status_result.consistency_level = ConsistencyLevel.QUORUM

        #pool = ThreadPool(4)
        pool = ThreadPool(2)
        #pool = ThreadPool(1)
        these = [(x,y,algorithm, session, status_result) for (x,y) in points]
        counts = pool.starmap(count_results, these)


        ####################################################################
        #
        # You can count the number of complete, incomplete, and missing
        # results like this:
        #
        ####################################################################

        complete   = [(x,y) for (x,y,a,c) in counts if (c == 10000)]
        incomplete = [(x,y) for (x,y,a,c) in counts if (c < 10000 and c > 0)]
        missing    = [(x,y) for (x,y,a,c) in counts if (c == 0)]

        print ('tile: ', tile, 'x: ', x, 'y: ', y,
               ', Complete: ', len(complete), ', Incomplete: ', len(incomplete), ', Missing: ', len(missing))

        if ((len(incomplete) > 0) and (len(incomplete) < 10)):
            print ('Incomplete X/Ys: ', incomplete)
        if ((len(missing) > 0) and (len(missing) < 10)):
            print ('Missing X/Ys; ', missing)


    if option == 'request':

        print ('Requesting Results...')
        #insert notebook methods to submit chips for pyccd processing here......

    if option == 'retrieve':

        ####################################################################
        #
        # Parent directory of json_name is assumed to exist.  Probably
        # should put that directory creation in here dynamically.  For now,
        # it is /data/<user>/sites, before branching off to inidividual
        # <site>/pyccd-results/<version_num>/json subdirectories.
        #
        # Hopefully, one can insert a chip or two or few instead of
        # 'complete' in the case where not all chips were complete, or not
        # all were successfully written for whatever reason (timeout).
        # One could do a slice with all x/y list and those that already
        # exist on disk and just extract those.
        #
        ####################################################################

        version_base, version_num = algorithm.split(':', 1)
        jsondir=os.environ["LCMAP_JSONDIR"]

        # temp testing
        #site_path = jsondir + '/{site}/pyccd-results'
        #results_path = site_path + '/{tile}/{version_num}'
        #json_path = results_path + '/json/{tile}_{x}_{y}.json'
        # end temp testing

        # lets do it all at once, shall we?
        json_name = jsondir + '/{site}/pyccd-results/{tile}/{version_num}/json/{tile}_{x}_{y}.json'

        print ('version_num: ', version_num)
        print ('json_name: ', json_name)

        print ('Extracting Results to .json...')
        print ('  in: ', json_name)


        ####################################################################
        #
        # Set consistency level.
        #
        ####################################################################

        ##status_result = session.prepare("SELECT * FROM results WHERE chip_x=? AND chip_y=? AND algorithm=?")
        ##status_result.consistency_level = ConsistencyLevel.QUORUM


        ####################################################################
        #
        # Again, be cautions with number of threads, but downloading all
        # 2,500 chips in a tile can take 90 min. with 4, longer with fewer.
        #
        ####################################################################

        save_pool  = ThreadPool(4)

        # H19V14 UL, for testing
        single = [( 284415, 1214805 )]
        save_these = [(json_name, site, tile, x, y, algorithm) for (x,y) in single]

        #save_these = [(json_name, tile, x, y, algorithm) for (x,y) in complete]

        results = save_pool.starmap(save_chip, save_these)


########################################################################
#
# Main entry point.
#
########################################################################

if __name__=='__main__':


    ####################################################################
    #
    # Parse args, exit upon error after message, else spit them out.
    #
    ####################################################################

    if len(sys.argv) == 6:
        site = sys.argv[1]
        h = int(sys.argv[2])
        v = int(sys.argv[3])
        algorithm = sys.argv[4]
        option = sys.argv[5]
    else:
        print ('')
        print ('Invalid number of args: ', len(sys.argv))
        print ('Usage: python manage_python_results.py <site> <h> <v> <algorithm> <option>')
        print ('')
        print ('The following environment variables must also be defined:')
        print ('    LCMAP_HOSTS')
        print ('    LCMAP_USERNAME')
        print ('    LCMAP_PASSWORD')
        print ('    LCMAP_KEYSPACE')
        print ('    LCMAP_JSONDIR')
        print ('')
        exit()

    print ('')
    print ('site:      ', site)
    print ('algorithm: ', algorithm)
    print ('h:         ', h)
    print ('v:         ', v)
    print ('option:    ', option)


    ####################################################################
    #
    # Small amount of argument checking.
    #
    ####################################################################

    if algorithm not in ('lcmap-pyccd:1.4.0rc1',
                         'lcmap-pyccd:2017.6.8',
                         'lcmap-pyccd:2017.06.20',
                         'lcmap-pyccd:2017.08.18',
                         'lcmap-pyccd:2017.10.27'):
        print ('Invalid algorithm: ', algorithm)
        exit()

    if option not in ('count', 'request', 'retrieve'):
        print ('Invalid option: ', option)
        exit()


    ####################################################################
    #
    # Start the work.
    #
    ####################################################################

    main(site, h, v, algorithm, option)
