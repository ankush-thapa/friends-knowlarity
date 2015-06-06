import pyorient
import utils

USERNAME = 'ankush'
PASSWORD = 'thapa'
DB_NAME = 'friends_db'
DB_LOCATION = "localhost"
DB_PORT = 2424

def get_db_client():
    client = pyorient.OrientDB(DB_LOCATION, DB_PORT)
    session_id = client.connect(USERNAME, PASSWORD)
    if not client.db_exists(DB_NAME, pyorient.STORAGE_TYPE_MEMORY ):
        client.db_create( DB_NAME, pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_MEMORY )
    client.db_open(DB_NAME, USERNAME, PASSWORD)
    init_db(client)
    return client

def close_db_client(g):
    if getattr(g, 'client', None):
        client = g.client
        client.db_close()
 
def init_db(client):
    try:
        command = "create class Users extends V"
        utils.execute_query(client, command)
    except:
        pass
    try:
        command = "create class Connections extends E"
        utils.execute_query(client, command)
    except:
        pass

def flush_db(client):
    client.db_drop(DB_NAME)
