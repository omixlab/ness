
from ness.models import models, BaseModel
import os
import json

def load_model(file_name:str) -> BaseModel:

    config_file_name = file_name + '.json'
    assert os.path.isfile(config_file_name)
    
    config = json.loads(open(config_file_name).read())
    model_type = config['model_type']
    return models[model_type].load(file_name)
