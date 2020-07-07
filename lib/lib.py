import os
import json

import jsonref

def list_files(folder):
    """
    List file names without extension in a folder
    """
    return [c for c in [".".join(f.split(".")[:-1]) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))] if c != ""]

def replace_methods(lib, key, obj):
    """
    Helper function that recursivly replaces values of key with matching function from lib in dicts.
    """
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = replace_methods(lib, key, v)
    if key in obj:
        obj[key] = getattr(lib, obj[key])
    return obj

def replace_parameters(obj, **kwargs):
    """
    Helper function that recursivly replaces values of key with matching function from lib in dicts.
    """
    if "$ref" in obj.keys():
        if len(obj.keys()) > 1:
            raise RuntimeError("Json $ref with other stuff in its dict!")
        ref = obj["$ref"]
        if ref[0] != "#":
            raise RuntimeError("Invalid json ref!")
        dictionary, key = ref[1:].split("/")
        return kwargs[dictionary][key]
    else:
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = replace_parameters(v, **kwargs)
    return obj