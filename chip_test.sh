#!/bin/bash

source ${HOME}/firebird_install/0.5

# 4 MS Priority Tiles
# tile, x, y, = 'H19V14', 284415, 1214805
# tile, x, y, = 'H20V14', 434415, 1214805
# tile, x, y, = 'H19V15', 284415, 1064805
# tile, x, y, = 'H20V15', 434415, 1064805

# tile, x, y, = 'H19V14', 284415, 1214805
#date;firebird-save -a 1980-01-01/2017-01-01 -b 284415,1214805 -p ccd -d 2016-01-01;date
#elapsed = 30:41, but local cassandra contention during the day?
#time firebird-save -a 1982-01-01/2015-12-31 -b 284415,1214805 -p ccd -d 2014-01-01 >& H19V14_284415_1214805.out
#elapsed = real    31m54.481s

# tile, x, y, = 'H20V14', 434415, 1214805
#time firebird-save -a 1982-01-01/2015-12-31 -b 434415,1214805 -p ccd -d 2014-01-01 >& H20V14_434415_1214805.out
#elapsed = real    26m54.230s

# tile, x, y, = 'H19V15', 284415, 1064805
#time firebird-save -a 1982-01-01/2015-12-31 -b 284415,1064805 -p ccd -d 2014-01-01 >& H19V15_284415_1064805.out
#elapsed = real    19m19.787s

# tile, x, y, = 'H20V15', 434415, 1064805
#time firebird-save -a 1982-01-01/2015-12-31 -b 434415,1064805 -p ccd -d 2014-01-01 >& H20V15_434415_1064805.out
#elapsed = real    18m51.383s

# download results
# python firebird_json_results.py

export v1=/lcmap_data/sites/ms/pyccd-results
export v2=/data2/bdavis/sites/ms/pyccd-results

# new docker; DB download; compare
#python compare_json_results.py $v1/H19V14/2017.08.18/json/H19V14_284415_1214805.json \
#                               $v2/H19V14/2017.10.27_DavisVM/json/H19V14_284415_1214805.json \
#                               0.00001

# good
#python compare_json_results.py $v1/H20V14/2017.08.18/json/H20V14_434415_1214805.json \
#                               $v2/H20V14/2017.10.27_DavisVM/json/H20V14_434415_1214805.json  \
#                               0.00001

#
#python compare_json_results.py $v1/H19V15/2017.08.18/json/H19V15_284415_1064805.json \
#                               $v2/H19V15/2017.10.27_DavisVM/json/H19V15_284415_1064805.json \
#                               0.00001

#
#python compare_json_results.py $v1/H20V15/2017.08.18/json/H20V15_434415_1064805.json \
#                               $v2/H20V15/2017.10.27_DavisVM/json/H20V15_434415_1064805.json \
#                               0.00001
