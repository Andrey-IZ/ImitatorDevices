import binascii
import struct


def byte2hex_str(byte_array):
    len_byte = len(byte_array)
    even_array = len_byte % 4 == 0
    str_format = '['
    hex_string = binascii.hexlify(byte_array).decode('ascii')
    for i, char in enumerate(hex_string):
        if not even_array and i % 2 == 0:
            str_format += ' '
        if even_array and i % 4 == 0:
            str_format += ' '
        str_format += char
    str_format += ' ] (' + str(len_byte) + ')'
    return str_format.upper()


def __convert_format_qt_types(type_value_str):
    fmt_str = ''
    if isinstance(type_value_str, str):
        type_value_str = type_value_str.lower().strip()
        if type_value_str.startswith('int', 2):
            if type_value_str.endswith('8'):
                fmt_str = 'b'
            elif type_value_str.endswith('16'):
                fmt_str = 'h'
            elif type_value_str.endswith('32'):
                fmt_str = 'i'
            elif type_value_str.endswith('64'):
                fmt_str = 'q'
            if type_value_str.find('u', 1, 2):
                fmt_str = fmt_str.upper()
        elif type_value_str == 'float':
            fmt_str = 'f'
        elif type_value_str == 'double':
            fmt_str = 'd'
    return '!' + fmt_str


def qt_value_to_bytes(type_str, value):
    fmt_str = __convert_format_qt_types(type_str)
    if fmt_str and value is not None:
        return struct.pack(fmt_str, value)
    raise TypeError('Invalid converting from qt type string')
