import handlers_ukcu as handlers


def test_ukcu_packet_parse(packet_bytes):
    packet = handlers.UkcuPacket()
    packet.parse(packet_bytes)
    return packet.code, packet.data


def test_ukcu_packet_to_bytes(code, data):
    packet = handlers.UkcuPacket(code, data)
    return packet.to_bytes()

def test_handler_response():
    b'\xa5\x00\x1b\x04\x01\x00\xff\x07\xe6\x17'
    data = handlers.handler_request_setup_ukcu()
    result = handlers.handler_ukcu_response(data[0][0], data[0] )
    assert data[0][0] == result

if __name__ == '__main__':
    assert test_ukcu_packet_parse(test_ukcu_packet_to_bytes(911, 112)) == (911, 112)
    test_handler_response()
    print("Ok")