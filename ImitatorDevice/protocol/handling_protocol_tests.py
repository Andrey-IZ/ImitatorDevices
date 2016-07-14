import importlib
import os
import re
import sys

import yaml
from ImitatorDevice.protocol.handling_protocol import HandlingProtocol
from tools_binary import str_hex2byte


def load_conf_test(filename):
    yml = yaml.load_all(open(filename))
    res = []
    for doc in yml:
        res.append(doc)
    return res


def request_parser(request):
    if not isinstance(request, str):
        return None
    str_packet_pure = re.sub(r'[: _]', '', request)
    strbyte = bytearray.fromhex(str_packet_pure)
    strhex = str_hex2byte(strbyte)
    print(strbyte, strhex)
    return strbyte


def load_handler(file_name, function_name):
    """
    Loads function-handler from file, which specify to configuration's file
    :param file_name:
    :param function_name:
    :return: function object of handler
    """
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
            print("Import error file_name: {0}, function_name: {1}".format(file_name, function_name))
    return None


def folding_settings_tests():
    settings = HandlingProtocol(None)
    settings.parse('protocol_serial_device.conf')
    assert settings.handler_response(
        b'\xa5\x00\x1b\x04\x01\x00\xff\x07\xe6\x17') == b'\xa5\x00\x1f\x04\x00\x00\x00\x00\x1b\x17'
    assert settings.handler_response(
        b'\xa5\x00\x1b\x04\x00\x00\x00\x00\x1f\x17') == b'\xa5\x00\x1f\x04\x00\x00\x00\x00\x1b\x17'


if __name__ == '__main__':
    for cmd in load_conf_test('protocol_serial_device.conf')[1:]:
        request = cmd.get('request')
        options = cmd.get('options', {'order': 'packet'})
        if isinstance(options, dict):
            handler_response = options.get('handler_response')
            handler_request = options.get('handler_request')
            func_handler_response = None
            func_handler_request = None
            if isinstance(handler_response, dict):
                print('handler_response')
                func_handler_response = load_handler(**handler_response)
            if isinstance(handler_request, dict):
                print('handler_request')
                func_handler_request = load_handler(**handler_request)
            if func_handler_response and func_handler_request and \
                    isinstance(request, list):
                for opt, value in options.iteritems():
                    if value == 'zip':
                        print('zip')
                    if value == 'packet':
                        print('packet')
                        for req in request:
                            request_parser(req)
            else:
                request_parser(request)