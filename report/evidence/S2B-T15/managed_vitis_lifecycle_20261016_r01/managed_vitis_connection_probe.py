import json
import os
import sys

import vitis

result_path = os.environ["S2B_MANAGED_VITIS_PROBE_RESULT"]
record = {"status": "FAIL", "mode": "OWN_SERVER_JOB", "port": int(os.environ["S2B_MANAGED_VITIS_PORT"]), "connect_called": False, "connected": False, "dispose_called": False, "channel_closed": False, "sdk_owned_server_pid": None}
client = None
server = None
try:
    client = vitis.create_client(port=record["port"], host="127.0.0.1", workspace=os.environ["S2B_MANAGED_VITIS_WORKSPACE"])
    record["connect_called"] = True
    server = client._serverObj
    record["connected"] = server.verify() is True and server.serverPort == record["port"] and server.host == "127.0.0.1"
    record["sdk_owned_server_pid"] = None if server.cp is None else server.cp.pid
    if not record["connected"] or server.cp is not None:
        raise RuntimeError("连接未落到本Run外部server")
finally:
    if client is not None:
        try:
            record["channel_closed"] = client.close() is True
        except BaseException as error:
            record["channel_close_error"] = repr(error)
    try:
        vitis.dispose()
        record["dispose_called"] = True
    except BaseException as error:
        record["dispose_error"] = repr(error)
    record["status"] = "PASS_SERVER_CLIENT_DISPOSE" if record["connected"] and record["dispose_called"] and record["channel_closed"] and record["sdk_owned_server_pid"] is None else "FAIL"
    with open(result_path, "x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
if record["status"] != "PASS_SERVER_CLIENT_DISPOSE":
    sys.exit(1)
