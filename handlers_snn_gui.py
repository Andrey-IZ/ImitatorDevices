#!/usr/bin/env python

from tools_binary import unpack_bits, pack_bits, BitArray, bit_array2endian_bytes
import sys


def big_endian_reverse(data_bytes):
    res_data_bytes = bytes()
    if sys.byteorder != 'big' and len(data_bytes) % 2 == 0:
        try:
            for i in range(1, len(data_bytes) + 1, 2):
                res_data_bytes += data_bytes[i:i + 1] + data_bytes[i - 1:i]
        except Exception as e:
            print("Error: Invalid data byte reverse (", e.args, ")", file=sys.stderr)
            return data_bytes
    return res_data_bytes


def handler_parser_snn_gui(bytes_recv):
    bytes_recv = big_endian_reverse(bytes_recv)
    packet_word = BitArray(bytes=bytes_recv[0:2])
    code = packet_word[8:16].unpack('uint:5, uint:1, uint:2')
    return code, bytes_recv


def handler_response_snn_gui_req_ak(log, parsing_data, request_data, response_data) -> [bytes]:
    codes = {0b00000: 'Останов', 0b00001: 'Вращение1', 0b00010: 'Вращение2',
             0b00101: 'Резерв1', 0b00110: 'Резерв2', 0b00111: 'Запрос АК',
             0b10000: 'Останов технологический', 0b10001: 'Вращение1 технологический',
             0b10010: 'Вращение2 технологический', 0b10011: 'Вращение Omega технологический',
             0b10100: 'Наведение технологический', 0b10101: 'Резерв1 технологический',
             0b10110: 'Резерв2 технологический', 0b10111: 'Запрос АК технологический',}
    code = parsing_data[0]
    send_data = []
    if code[0] in codes:
        log.info('++ Команда: \"{}\"'.format(codes[code[0]]))
        packet_word1 = BitArray(length=16)
        packet_word2 = BitArray(length=16)
        packet_word1[8:16] = pack_bits('uint:5, uint:1, uint:2', code[0], code[1], code[2]).uint
        data = bit_array2endian_bytes([packet_word1, packet_word2])
        data = big_endian_reverse(data)
        send_data.append(data)

    return send_data


def handler_response_snn_gui_req_turn_omega(log, parsing_data, request_data, response_data) -> [bytes]:
    code, bytes_recv = parsing_data
    send_data = []
    if code[0] == request_data:
        packet_techno_word1 = BitArray(bytes=bytes_recv[0:2])
        packet_techno_word2 = BitArray(bytes=bytes_recv[2:4])
        omega_10bit = BitArray(uint=packet_techno_word1[0:7].uint, length=10)
        omega_high = (omega_10bit << 3).uint
        omega_low = packet_techno_word2[13:16].uint
        sign_omega = 1 if packet_techno_word1[7] else -1
        omega = int(omega_high | omega_low)
        omega *= sign_omega
        log.info('++ Команда: \"Вращение ω={}\"'.format(omega))

        packet_word1 = BitArray(length=16)
        packet_word2 = BitArray(length=16)
        packet_word1[8:16] = pack_bits('uint:5, uint:1, uint:2', code[0], code[1], code[2]).uint
        data = bit_array2endian_bytes([packet_word1, packet_word2])
        data = big_endian_reverse(data)
        send_data.append(data)

    return send_data


def handler_response_snn_gui_aim_on(log, parsing_data, request_data, response_data) -> [bytes]:
    code, bytes_recv = parsing_data
    send_data = []
    if code[0] == request_data:
        packet_techno_word1 = BitArray(bytes=bytes_recv[0:2])
        packet_techno_word2 = BitArray(bytes=bytes_recv[2:4])
        betta_12bit = BitArray(uint=packet_techno_word1[0:8].uint, length=12)
        betta_high = (betta_12bit << 4).uint
        betta_low = packet_techno_word2[12:16].uint
        betta_hex = int(betta_high | betta_low)
        k_angle = 360.0 / 4095
        betta_degree = round(betta_hex * k_angle, 2)
        log.info('++ Команда ({2}): \"Наведение, β={0} (0x{1:X})\"'.format(betta_degree, betta_hex, bin(code[0])))

        packet_word1 = BitArray(length=16)
        packet_word2 = BitArray(length=16)
        packet_word1[8:16] = pack_bits('uint:5, uint:1, uint:2', code[0], code[1], code[2]).uint
        data = bit_array2endian_bytes([packet_word1, packet_word2])
        data = big_endian_reverse(data)
        send_data.append(data)

    return send_data
