#!/bin/bash

########################################################################
#
# change_maps.sh
#
# Shell script wrapper around the python application
# which produces visual change map products from pyccd results stored
# in .json disk files, after extraction from the Cassandra Data Base.
#
# This allows for parameter passing, chaining multiple script/functions
# toghether, capturing stdout/stderr to log files, prepending invocation
# with sleep, etc., etc.
#
########################################################################

########################################################################
#
# One-time setup of virtual environment and git repo.
#
# set up the virtual environment
# previous
#    conda env create -f /lcmap_data/scripts/envs/json-matlab-env.yml
# 20170825
#    conda env create -f /data2/klsmith/json-matlab-py3-env.yml
#
# To activate this environment, use:
#    source activate json-matlab3
#
# get the master repo, which makes the necessary sub-directory....
#     cd 
#     git clone https://github.com/klsmith-usgs/json-matlab.git
#
########################################################################

########################################################################
# receive args, tile/dir names can be constructed from h,v
########################################################################

if [ "$#" -ne 4 ]; then
    echo ""
    echo Invalid Number of Arguments: $#
    echo "Usage: change_maps.sh <site> <version> <h> <v>"
    echo "Example: change_maps.sh ms 2018.08.18 19 14"
    exit -1
    echo ""
fi

site=$1
version=$2
h=$3
v=$4

########################################################################
# Regurgitate.
########################################################################

x=`printf "%02d" $h`
y=`printf "%02d" $v`
tile="H"$x"V"$y

########################################################################
#
# when downloading .json with VM iPython notebook, files are placed on
# /data2.  rsync transfer to /lcmap data is required first if running
# change_maps from eval server.  If running change_maps from scp40, both
# /data2 and /lcmap_data are nfs mounted.  In that case, run change_maps
# on /data2, them mv to /lcmap_data afterward
#
# Also, .mat and log1 are only needed if using previous version of 
# json-matlab distribution.  Current version reads .json and produces
# .tif directly
#
########################################################################

lcmap_dir=/lcmap_data/sites/$site/pyccd-results/$tile/$version
data2_dir=/data2/${USER}/pyccd-results/$site/$tile/$version

log=/data2/${USER}/logs/change_maps
mkdir -p $log

json_in=$data2_dir/json
#json_in=$lcmap_dir/json

#matlab_out=$dir/mat

#change_out=$data2_dir/tif
change_out=$lcmap_dir/tif

#log1=$log/$tile"_mat.out"
log2=$log/$tile"_change_maps.txt"

h=$h
v=$v

#mkdir -p $matlab_out
mkdir -p $change_out


#num_cpus=20
# no, leave a couple processors for doing other stuff.
num_procs=`grep processor /proc/cpuinfo|wc -l`
num_cpus=`echo $num_procs -2 | bc -l`

########################################################################
# Go do the location of the distribution. Display parameters.
########################################################################

cd ${HOME}/json-matlab

echo "json Input Directory:        " $json_in
echo "Change Map Output Directory: " $change_out
echo "Number of CPUs Requested:    " $num_cpus
echo "Horizontal Tile Index:       " $h
echo "Vertical Tile Index:         " $v
echo "Log File:                    " $log2

########################################################################
# Call the python client that will do the work.
########################################################################

python change_products-cli.py $json_in \
                              $change_out \
                              $h \
                              $v \
                              -p $num_cpus >& $log2 &

########################################################################
# 
# Afterward, you may have to:
# mv $data2_dir/json/*.json $lcmap_dir/json/.
# if tifs were written to /data2:
# mv $data2_dir/tif/*.tif $lcmap_dir/tif/.
# 
########################################################################

exit 0






# former version requiring intermediate matlab file generation
echo "json Input Directory:     " $json_in
echo "Matlab Output Directory:  " $matlab_out
echo "Number of CPUs Requested: " $num_cpus
echo "Horizontal Tile Index:    " $h
echo "Vertical Tile Index:      " $v
echo "Log File:                 " $log1

python matlab-cli.py -i $json_in \
                     -p $num_cpus \
                     $matlab_out \
                     $h \
                     $v \
                     "lcmap-pyccd:2017.6.8" >& $log1

echo "Matlab Input Directory:      " $matlab_out
echo "Change Map Output Directory: " $change_out
echo "Number of CPUs Requested:    " $num_cpus
echo "Horizontal Tile Index:       " $h
echo "Vertical Tile Index:         " $v
echo "Log File:                    " $log2

python products-cli.py $matlab_out \
                       $change_out \
                       $h \
                       $v \
                       -p $num_cpus >& $log2 &

exit 0

