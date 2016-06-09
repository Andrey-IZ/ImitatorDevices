import binascii
import struct
import bitstring
from bitstring import BitArray


def bit_array2endian_bytes(packet_word_list):
    data = bytearray()
    for word in packet_word_list:
        # if sys.byteorder != 'big':
        #     word.byteswap()
        data.extend(word.tobytes())
    return bytes(data)


def unpack_bits(byte_array, fmt, **kwargs):
    ba = BitArray(bytes=byte_array)
    result = ba.unpack(fmt, **kwargs)
    return result


def pack_bits(fmt, *values, **kwargs):
    return bitstring.pack(fmt, *values, **kwargs)


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
        elif type_value_str == 'bool':
            fmt_str = 'B'
    return '!' + fmt_str


def qt_value_to_bytes(type_str, value):
    try:
        fmt_str = __convert_format_qt_types(type_str)
        if fmt_str and value is not None:
            return struct.pack(fmt_str, value)
    except Exception as err:
        raise TypeError(
            'Invalid converting from qt type string: {} ({}) <= {}'.format(value, type(value), err)) from err


def value_from_qt_bytes(type_str, byte_array):
    try:
        fmt_str = __convert_format_qt_types(type_str)
        if fmt_str and byte_array is not None:
            return struct.unpack(fmt_str, byte_array)[0]
    except Exception as err:
        raise TypeError('Invalid converting from qt type string: {} ({}) <= {}'.format(
            byte_array, type(byte_array), err)) from err
