from ansys.dpf.sound.server_helpers import connect_to_or_start_server, validate_dpf_sound_connection


def test_validate_dpf_sound_connection():
    validate_dpf_sound_connection()


def test_connect_to_or_start_server():
    s = connect_to_or_start_server(port="6780", ip="127.0.0.1")
    print(s)
