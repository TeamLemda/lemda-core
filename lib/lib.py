import os
import json
import collections

import jsonref

class Feedback():
    output = None
    feedback = None

    def __init__(self, output, feedback):
        self.output = output
        self.feedback = feedback

    def __getitem__(self, x):
        return getattr(self, x)

    def __str__(self):
        return str(self.output)

class BlockError(RuntimeError):
    pass

def format_list(arguments, **kwargs):
    """
    Using format strings, fills in a block's arguments values.
    """
    output = []
    for arg in arguments:
        if isinstance(arg, str):
            output.append(format_params(arg, **kwargs))
        elif isinstance(arg, dict):
            output.append(format_dict(arg, **kwargs))
        elif isinstance(arg, list):
            output.append(format_list(arg, **kwargs))
    return output


def format_dict(arguments, **kwargs):
    """
    Using format strings, fills in a block's arguments values.
    """
    for arg_name, arg in arguments.items():
        if isinstance(arg, str):
            arguments[arg_name] = format_params(arg, **kwargs)
        elif isinstance(arg, dict):
            arguments[arg_name] = format_dict(arg, **kwargs)
        elif isinstance(arg, list):
            arguments[arg_name] = format_list(arg, **kwargs)
    return arguments

def format_params(string, **dicts):
    if len(string) < 3:
        return string
    
    if string[0] != "{" or string[1] == "{" or string[-1] != "}" or string[-2] == "}":
        return format_params_nonobj(string, **dicts)

    path = string[1:-1].split(".")
    curr = dicts
    while len(path) > 0:
        curr = curr[path.pop(0)]
    if isinstance(curr, Feedback):
        curr = curr.output
    return curr

def format_params_nonobj(string, **dicts):
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self
    def to_attrdict(dicts):
        attrdicts = {}
        for k, v in dicts.items():
            if isinstance(v, dict):
                attrdicts[k] = to_attrdict(v)
            else:
                attrdicts[k] = v
        return AttrDict(attrdicts)
    return string.format(string, **to_attrdict(dicts))

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