from cassandra.cluster import Cluster, ExecutionProfile
from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import ordered_dict_factory
from datetime import datetime
import json

def setup_session(username, password, hosts, keyspace):
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(hosts, auth_provider=auth_provider)
    session = cluster.connect(keyspace)
    session.row_factory = ordered_dict_factory
    session.default_consistency_level = ConsistencyLevel.QUORUM
    session.default_timeout = 30.0
    return session

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def get_chip(x, y):
    return session.execute(result_cql, (x, y))

def save_chip(path_template, x, y,):
    path = path_template.format(x=x,y=y)
    result = session.execute(result_cql, (x, y))
    with open(path.format(x=x,y=y),'w') as outfile:
        json.dump(list(result), outfile, default=json_serial)
    return path

# MS
site = 'ms'
# tile, x, y, = 'H19V14', 284415, 1214805
# tile, x, y, = 'H20V14', 434415, 1214805
# tile, x, y, = 'H19V15', 284415, 1064805
tile, x, y, = 'H20V15', 434415, 1064805

# Brian's VM host
username='cassandra'
password='cassandra'
hosts=['10.0.84.207']
keyspace='lcmap_changes_local'

session = setup_session(username, password, hosts, keyspace)

result_cql = session.prepare("SELECT * FROM lcmap_pyccd_2017_10_27 WHERE chip_x=? AND chip_y=?")
#result_cql = session.prepare("SELECT * FROM lcmap_pyccd:2017.10.27 WHERE chip_x=? AND chip_y=?")

#save_chip("/data2/bdavis/sites/ms/pyccd-results/H19V14/2017.10.27_DavisVM/json/H19V14_{x}_{y}.json", 284415, 1214805)
#save_chip("/data2/bdavis/sites/ms/pyccd-results/H20V14/2017.10.27_DavisVM/json/H20V14_{x}_{y}.json", 434415, 1214805)
#save_chip("/data2/bdavis/sites/ms/pyccd-results/H19V15/2017.10.27_DavisVM/json/H19V15_{x}_{y}.json", 284415, 1064805)
save_chip("/data2/bdavis/sites/ms/pyccd-results/H20V15/2017.10.27_DavisVM/json/H20V15_{x}_{y}.json", 434415, 1064805)
