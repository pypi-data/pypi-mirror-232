import json
from copy import deepcopy

import y_py as Y

from yroom import YRoomClientOptions, YRoomManager


def tob(num: int):
    return num.to_bytes(1, "big")


def test_connect():
    room_name = "test"
    manager = YRoomManager()
    message = manager.connect(room_name, 1)
    assert len(message.payloads) > 0
    assert len(message.broadcast_payloads) == 0
    assert manager.has_room(room_name)
    assert manager.is_room_alive(room_name)
    assert manager.list_rooms() == [room_name]
    manager.remove_room(room_name)
    assert not manager.has_room(room_name)
    assert manager.list_rooms() == []


def test_connect_with_data():
    d1 = Y.YDoc()
    text = d1.get_text("test")
    with d1.begin_transaction() as txn:
        text.extend(txn, "hello world!")
    update_data = Y.encode_state_as_update(d1)

    room_name = "test"
    manager = YRoomManager()
    message = manager.connect_with_data(room_name, 1, update_data)
    assert len(message.payloads) > 0
    assert len(message.payloads) > 0
    assert len(message.broadcast_payloads) == 0
    assert manager.serialize_room(room_name) == update_data


def test_disconnect():
    room_name = "test"
    conn_id = 1
    manager = YRoomManager()
    manager.connect(room_name, conn_id)
    assert manager.has_room(room_name)
    assert manager.is_room_alive(room_name)
    message = manager.disconnect(room_name, conn_id)
    assert len(message.payloads) == 0
    assert len(message.broadcast_payloads) > 0
    assert not manager.is_room_alive(room_name)
    assert manager.list_rooms() == [room_name]
    manager.remove_room(room_name)
    assert not manager.has_room(room_name)
    assert manager.list_rooms() == []


def test_connect_multiple():
    room_name = "test"
    conn_id_1 = 1
    conn_id_2 = 2
    manager = YRoomManager()
    manager.connect(room_name, conn_id_1)
    manager.connect(room_name, conn_id_2)
    assert manager.is_room_alive(room_name)
    manager.disconnect(room_name, conn_id_1)
    assert manager.is_room_alive(room_name)
    manager.disconnect(room_name, conn_id_2)
    assert not manager.is_room_alive(room_name)


def test_extraction():
    d1 = Y.YDoc()
    text = d1.get_text("text")
    test_text = "hello world!"
    array = d1.get_array("array")
    test_array = [1, "foo", True]
    map = d1.get_map("map")
    test_map = {"a": 1}
    xml_element = d1.get_xml_element("xml_element")
    with d1.begin_transaction() as txn:
        text.extend(txn, test_text)
        array.extend(txn, test_array)
        map.update(txn, test_map)

        b = xml_element.push_xml_text(txn)
        a = xml_element.insert_xml_element(txn, 0, "p")
        aa = a.push_xml_text(txn)
        aa.push(txn, "hello")
        b.push(txn, "world")

    update_data = Y.encode_state_as_update(d1)

    room_name = "test"
    manager = YRoomManager()
    manager.connect_with_data(room_name, 1, update_data)
    assert manager.export_text(room_name, "text") == test_text
    assert json.loads(manager.export_array(room_name, "array")) == test_array
    assert json.loads(manager.export_map(room_name, "map")) == test_map
    assert (
        manager.export_xml_element(room_name, "xml_element")
        == "<xml_element><p>hello</p>world</xml_element>"
    )


def test_server_sync():
    d1 = Y.YDoc()
    text = d1.get_text("test")
    with d1.begin_transaction() as txn:
        text.extend(txn, "hello world!")

    room_name = "test"
    client_id = 1
    manager = YRoomManager()
    message = manager.connect(room_name, client_id)
    initial_payload = b"".join(
        [
            b"\x00\x00",  # sync step 1
            b"\x01",  # len message
            b"\x00",  # zero length state vector
        ]
    )
    assert message.payloads == [initial_payload]
    with d1.begin_transaction() as txn:
        diff = txn.diff_v1(None)

    payload = b"".join(
        [
            b"\x00\x01",  # sync step 2
            len(diff).to_bytes(1, "big"),  # len of diff
            diff,  # the diff
        ]
    )
    message = manager.handle_message(room_name, client_id, payload)
    assert message.payloads == []
    assert message.broadcast_payloads == []
    assert manager.export_text(room_name, "test") == "hello world!"


def test_server_no_sync_start():
    empty = Y.YDoc()
    d1 = Y.YDoc()
    text = d1.get_text("test")
    with d1.begin_transaction() as txn:
        text.extend(txn, "hello world!")

    room_name = "test"
    client_id = 1
    manager = YRoomManager({room_name: {"SERVER_START_SYNC": False}})
    message = manager.connect(room_name, client_id)
    assert message.payloads == []
    assert message.broadcast_payloads == []

    state_vector = Y.encode_state_vector(d1)
    sv_len = len(state_vector).to_bytes(1, "big")
    client_sync_step1_payload = b"".join(
        [
            b"\x00\x00",  # sync step 1
            sv_len,
            state_vector,
        ]
    )
    message = manager.handle_message(room_name, client_id, client_sync_step1_payload)

    # Simulate empty document diff with d1
    with empty.begin_transaction() as txn:
        diff = txn.diff_v1(state_vector)
    len_diff = len(diff).to_bytes(1, "big")

    empty_sv = Y.encode_state_vector(empty)
    empty_sv_len = len(empty_sv).to_bytes(1, "big")

    assert message.payloads == [
        b"".join(
            [
                b"\x00\x01",  # sync step 2
                len_diff,  # len of buffer
                diff,  # diffed update
                b"\x00\x00",  # sync step 1
                empty_sv_len,
                empty_sv,
                b"\x01\x01\x00",  # empty awareness update
            ]
        )
    ]
    assert message.broadcast_payloads == []


def test_client_prefix_no_pipeline():
    """
    TipTap HocusPocus Collaboration uses a prefix in protocol messages
    and does not support pipelining.
    """
    d1 = Y.YDoc()
    empty = Y.YDoc()
    name = "test"
    prefix = b"".join([len(name).to_bytes(1, "big"), name.encode("utf-8")])
    text = d1.get_text(name)
    with d1.begin_transaction() as txn:
        text.extend(txn, "hello world!")

    room_name = "test"
    client_id = 1
    manager = YRoomManager(
        {
            room_name: {
                "SERVER_START_SYNC": False,
                "PROTOCOL_NAME_PREFIX": True,
                "PROTOCOL_DISABLE_PIPELINING": True,
            }
        }
    )
    message = manager.connect(room_name, client_id)
    assert message.payloads == []
    assert message.broadcast_payloads == []

    state_vector = Y.encode_state_vector(d1)
    sv_len = len(state_vector).to_bytes(1, "big")
    client_sync_step1_payload = b"".join(
        [
            prefix,
            b"\x00\x00",  # sync step 1
            sv_len,
            state_vector,
        ]
    )

    empty_sv = Y.encode_state_vector(empty)
    empty_sv_len = len(empty_sv).to_bytes(1, "big")

    message = manager.handle_message(room_name, client_id, client_sync_step1_payload)
    assert message.payloads == [
        b"".join(
            [
                prefix,
                b"\x00\x01",  # sync step 2
                b"\x02",  # len of buffer
                b"\x00\x00",  # diffed update
            ]
        ),
        b"".join(
            [
                prefix,
                b"\x00\x00",  # sync step 1
                empty_sv_len,
                empty_sv,
            ]
        ),
        b"".join(
            [
                prefix,
                b"\x01\x01\x00",  # empty awareness update
            ]
        ),
    ]

    assert message.broadcast_payloads == []


def test_update():
    base_doc = Y.YDoc()
    text_name = "test"
    room_name = "test"
    text = base_doc.get_text(text_name)
    with base_doc.begin_transaction() as txn:
        text.extend(txn, "hello world!")
    update_data = Y.encode_state_as_update(base_doc)

    manager = YRoomManager()
    manager.connect_with_data(room_name, 1, update_data)

    with base_doc.begin_transaction() as txn:
        text.extend(txn, " goodbye!")
    changed_data = Y.encode_state_as_update(base_doc)

    payload = b"".join(
        [
            b"\x00\x02",  # update
            len(changed_data).to_bytes(1, "big"),  # len of update
            changed_data,  # the update
        ]
    )

    message = manager.handle_message(room_name, 1, payload)
    assert message.payloads == []
    assert message.broadcast_payloads == [payload]
    assert manager.export_text(room_name, text_name) == "hello world! goodbye!"


def test_client_read_only():
    base_doc = Y.YDoc()
    text_name = "test"
    room_name = "test"
    client_id = 1
    text = base_doc.get_text(text_name)
    with base_doc.begin_transaction() as txn:
        text.extend(txn, "hello world!")
    update_data = Y.encode_state_as_update(base_doc)

    manager = YRoomManager()
    manager.connect_with_data(room_name, 1, update_data)

    with base_doc.begin_transaction() as txn:
        text.extend(txn, " goodbye!")

    options = YRoomClientOptions(allow_write=False)

    # Try sending sync step 2 with read-only client
    with base_doc.begin_transaction() as txn:
        diff = txn.diff_v1(None)

    payload = b"".join(
        [
            b"\x00\x01",  # sync step 2
            len(diff).to_bytes(1, "big"),  # len of diff
            diff,  # the diff
        ]
    )
    message = manager.handle_message(room_name, client_id, payload, options)
    assert message.payloads == []
    assert message.broadcast_payloads == []
    assert manager.export_text(room_name, text_name) == "hello world!"

    # Try writing update with read_only client
    changed_data = Y.encode_state_as_update(base_doc)
    payload = b"".join(
        [
            b"\x00\x02",  # update
            len(changed_data).to_bytes(1, "big"),  # len of update
            changed_data,  # the update
        ]
    )
    message = manager.handle_message(room_name, client_id, payload, options)
    assert message.payloads == []
    assert message.broadcast_payloads == []
    assert manager.export_text(room_name, text_name) == "hello world!"


def test_client_awareness():
    room_name = "test"
    client_1 = 1
    client_2 = 2
    client_3 = 3
    manager = YRoomManager({room_name: {"SERVER_START_SYNC": False}})
    message = manager.connect(room_name, client_1)
    assert message.payloads == []
    assert message.broadcast_payloads == []

    def make_client(client_id):
        return b"".join(
            [
                tob(client_id),  # client id
                tob(1),  # client clock
                tob(2),  # length of json
                b"{}",  # json
            ]
        )

    def make_awareness_update(clients):
        awareness_update = b"".join(
            [
                tob(len(clients)),  # number of clients
            ]
            + clients
        )
        return b"".join(
            [b"\x01", tob(len(awareness_update)), awareness_update]  # update
        )

    payload_1 = make_awareness_update([make_client(client_1)])
    message = manager.handle_message(room_name, client_1, payload_1)
    assert message.payloads == []
    assert message.broadcast_payloads == [payload_1]

    message = manager.connect(room_name, client_2)
    assert message.payloads == [payload_1]
    assert message.broadcast_payloads == []

    message = manager.connect(room_name, client_2)
    payload_2 = make_awareness_update([make_client(client_1), make_client(client_2)])
    message = manager.handle_message(room_name, client_2, payload_2)
    assert message.payloads == []
    assert make_client(client_1) in message.broadcast_payloads[0]
    assert make_client(client_2) in message.broadcast_payloads[0]

    # Test that client 3 cannot write awareness update
    payload_3 = make_awareness_update(
        [
            make_client(client_1),
            make_client(client_2),
            make_client(client_3),
        ]
    )
    options = YRoomClientOptions(allow_write_awareness=False)
    message = manager.handle_message(room_name, client_3, payload_3, options)
    assert message.payloads == []
    assert message.broadcast_payloads == []


def test_pickle_client_options():
    options = YRoomClientOptions(allow_write=False, allow_write_awareness=False)
    copied_options = deepcopy(options)
    assert copied_options.allow_write is False
    assert copied_options.allow_write_awareness is False
