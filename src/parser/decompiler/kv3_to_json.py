import sys
import os
import keyvalues3 as kv3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils import json_utils

# Recursively accesses all nested objects and hosts json-serializable values in the returned dict
def kv3_to_dict(kv3_obj):
    # Include all items that are dicts
    dict = {}

    # If cannot access attributes, end recursion
    try:
        items = kv3_obj.items()
    except AttributeError:
        return None
    
    for key, value in items:
        if not json_utils.is_json_serializable(value): # Only include values that are json serializable
            try:
                value = kv3_to_dict(value)
                if value is None:
                    continue # Continue to next value if its not serializable
            except TypeError:
                return None

        dict[key] = value

    return dict


# Converts kv3 object to dict, then writes dict to json
def kv3_to_json(kv3_obj, output_file):
    # output_file should always end in .json
    if not output_file.endswith('.json'):
        raise ValueError('output_file must end in .json')
    
    return json_utils.write(output_file, kv3_to_dict(kv3_obj))


if __name__ == '__main__':
    print('---', sys.argv[1])

    with open(sys.argv[1], 'r') as f:
        content = f.read()
        # subclass features in kv3 don't seem to be supported in the keyvalues3 python library
        content = content.replace('subclass:', '') 

    with open(sys.argv[1], 'w') as f:
        f.write(content)

    #print('Starting vdata_path:', vdata_path)
    data = kv3.read(sys.argv[1])
    out_path = sys.argv[1].replace('/vdata','').replace('.vdata','.json')
    #print('Finished out_path:', out_path)
    kv3_to_json(data, out_path)
