# Project Title

postProcessing contains python and bash shell scripts for creation of visual change products (change map .tif files) from PyCCD (Python Condinuous Change Detection) results, including some Q/A steps for the LCMAP (Land Change Monitoring And Projection) project.

## Getting Started

These scripts have been implemented and tested with linux:

&nbsp;&nbsp;2.6.32-696.13.2.el6.x86_64 #1 SMP Thu Oct 5 21:22:16 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux

and python:


&nbsp;&nbsp;Python 3.4.5  
&nbsp;&nbsp;Python 3.6.2
  
### Prerequisites

These scripts are run from a linux command line, and logging is accomplished by redirecting stdin and stdout.

### Installing

The following virtual environment modules are required for the superset of all python scripts and functions:

pip freeze:

&nbsp;&nbsp;cassandra-driver==3.10  
&nbsp;&nbsp;GDAL==2.2.1  
&nbsp;&nbsp;numpy==1.13.1  
&nbsp;&nbsp;PyYAML==3.12  
&nbsp;&nbsp;requests==2.14.2  
&nbsp;&nbsp;scikit-learn==0.19.0  
&nbsp;&nbsp;scipy==0.19.1  
&nbsp;&nbsp;six==1.11.0  

'pip install' can be used to set up the virtual environmet.  For example:

```
pip install cassandra-driver==3.10
```
etc., ....

Scripts should be placed in a directory known by $PATH and/or $PYTHONPATH, and/or invoked after cd to cwd.

## Running the scripts

More detailed information is available in:

lcmap_pyccd_ postprocessing_steps.pdf


To poll the progress of PyCCD processing of an ARD tile, and/or download completed results, manage_pyccd_results.py can be used:

```
Usage: python manage_python_results.py <site> <h> <v> <algorithm> <option>

The following environment variables must also be defined:
    LCMAP_HOSTS
    LCMAP_USERNAME
    LCMAP_PASSWORD
    LCMAP_KEYSPACE
    LCMAP_JSONDIR
	
"options" include:
    "count" to poll the number of complete, in-progress, and incomplete X-Y locations in the tile
	"request" to initate processing of the tile
	"retrieve" to download completed results for the tile to the local file system in JSON format
```
	
After PyCCD has been completed for an ARD tile, and the results dowloaded from the CASSANDRA data base to a local file system .json file, some Q/A to ensure valud results exist for all 10,000 X-Y locations in the tile can be performed:

```
python count_json_results.py <path-to-.json-files>
```

Any of the 10,000 X-Y locations which do not have valid results will be reported to stdout.


To compare .json files from to differing versions or tests of PyCCD, compare_json_results.py can be used with a tolerance value argument to ensure the computed values are compatible:

```
python compare_json_results.py <first-.json-file> <second-.json-file> <tolerance_value>
Example: python compare_json_results.py H19V14_284415_1214805_v1.json H19V14_284415_1214805_v2.json 0.000001
```

Any X-Y locations which have non-numerical elements which do not match, or numerical entries that do not match within the input tolerance value will be reported to stdout.


After the results for a tile have been verifed, visual change map products (.tif maps) can be generated with change_maps.sh:

```
Usage: change_maps.sh <site> <version> <h> <v>
Example: change_maps.sh ms 2018.08.18 19 14
```

Input .json files and output products curretnly assume directory structures of, based on the systems used for product analysis:  

&nbsp;&nbsp;/data2/${USER}/pyccd-results/$site/$tile/$version  
&nbsp;&nbsp;/lcmap_data/sites/$site/pyccd-results/$tile/$version  

These should probably be an argument or env var.

## Deployment

Deployment and use of this software assumes access to necessary JSON-formatted data files.


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

TBD

## Authors

* **Brian N. Davis** - *Initial work* - [CrustyQuarrier](https://github.com/CrustyQuarrier/postProcessing)

See also the list of contributors (https://github.com/USGS-EROS/lcmap-pyccd/graphs/contributors) who participated in this project.

## License

SGT, Inc., Contractor to the USGS EROS Center. 47914 252nd Street, Sioux Falls, SD 57198.
Work performed under USGS contract G15PC00012.
All USGS open source licensing applies.

## Acknowledgments

Thanks to:  
&nbsp;&nbsp;David Hill  
&nbsp;&nbsp;Jon Morton  
&nbsp;&nbsp;Clay Austin  
&nbsp;&nbsp;Kelcy Smith  
&nbsp;&nbsp;Calli Jenkerson  
