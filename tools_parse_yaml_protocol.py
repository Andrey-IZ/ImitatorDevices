
import yaml
import re
import sys
import os
import importlib


def load_conf_test(filename):
    yml = yaml.load_all(open(filename))
    res = []
    for doc in yml:
        res.append(doc)
    return res


def load_handler(file_name, function_name):
    """
    Loads function-handler from file, which specify to configuration's file
    :param file_name:
    :param function_name:
    :return: function object of handler
    """
    if isinstance(function_name, list):
        list_func = list()
        for function in function_name:
            list_func.append(__import_function(file_name, function))
        return list_func
    else:
        return [__import_function(file_name, function_name)]


def __import_function(file_name, function_name):
    if isinstance(file_name, str) and isinstance(function_name, str):
        path_file = os.path.abspath(file_name)
        module_name = os.path.basename(path_file)[:-3] if file_name.endswith('.py') else os.path.basename(path_file)
        path_dir = os.path.dirname(path_file).split('\\')[-1]
        if path_dir not in sys.path:
            sys.path.append(path_dir)
        try:
            module = importlib.import_module(module_name)
            func = getattr(module, function_name, None)
            return func
        except ImportError:
            raise ImportError("Error import funcion: '{1}' from file name: '{0}'".format(file_name, function_name))


def str_hex2byte(request):
    if not isinstance(request, str):
        return None

    str_packet_pure = re.sub(r'[^A-Za-z0-9]', '', request)
    try:
        bytes_req = bytes.fromhex(str_packet_pure)
    except ValueError as e:
        raise ValueError("Error convert string to bytes: before={}; after={}; {}".format(request, str_packet_pure, e.args))

    return bytes_req


def str_dict_keys_lower(dict_option):
    """

    :type dict_option: object
    """
    if isinstance(dict_option, dict) and dict_option:
        for k, v in dict_option.items():
            if not str(k).islower():
                dict_option[k.lower()] = v
                del dict_option[k]

    return dict_option