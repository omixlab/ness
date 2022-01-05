from ness.databases import databases, BaseDatabase
import os
import json

def load_database(file_name:str) -> BaseDatabase:

    config_file_name = os.path.join(file_name, 'database.json')
    assert os.path.isfile(config_file_name)
    
    config = json.loads(open(config_file_name).read())
    database_type = config['database_type']
    return databases[database_type].load(file_name)