import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from utils.config_manager import get_config_value
import utils.json_utils as json_utils
import json


class Resource:
    output_path = get_config_value('OUTPUT_DIR')
    resource_path = os.path.join(output_path, 'resources')

    # Save all object's of a given class from memory to json file
    @classmethod
    def save_objects(cls, free_memory=True):
        class_name_str = cls.__name__

        os.makedirs(Resource.resource_path, exist_ok=True)
        path = os.path.join(Resource.resource_path, class_name_str + '.json')

        # Convert hash of objects to hash of hashes
        hash = {}
        for obj_key, obj in cls.objects.items():
            for attr in obj.__dict__['data']:
                if obj_key not in hash:
                    hash[obj_key] = {}
                hash[obj_key][attr] = obj.data[attr]

        # Write to file
        json_utils.write(path, hash)

        if free_memory:
            cls.objects = {}

    # Load all object's of a given class from json file to memory
    @classmethod
    def load_objects(cls):
        class_name_str = cls.__name__

        os.makedirs(Resource.resource_path, exist_ok=True)
        path = os.path.join(Resource.resource_path, class_name_str + '.json')

        # Convert hash of hashes to hash of objects
        with open(path) as json_file:
            data = json.load(json_file)
            for obj_key, obj_data in data.items():
                obj = cls(obj_key)
                obj.data = obj_data

    @classmethod
    def hash_to_objs(cls, hash):
        for key, value in hash.items():
            obj = cls(key)
            obj.data = value

    # Placeholder for use in ChangelogsParser
    # After changelog rework, this will be removed
    @classmethod
    def objs_to_hash(cls):
        hash = {}
        for obj_key, obj in cls.objects.items():
            for attr in obj.__dict__['data']:
                if obj_key not in hash:
                    hash[obj_key] = {}
                hash[obj_key][attr] = obj.data[attr]
        return hash

    def get_prop(self, prop):
        return self.data.get(prop, None)
