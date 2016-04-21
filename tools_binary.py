import binascii


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
