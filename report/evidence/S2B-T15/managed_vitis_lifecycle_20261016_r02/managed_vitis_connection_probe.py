import hashlib
import json
import os
import sys

import vitis
from vitis import _server

expected_sdk_sha = "2dc671f21afcaefa3223c125c5a1cdcdbebdd9fda4360b4e38bd99c92214e368"
result_path = os.environ["S2B_MANAGED_VITIS_PROBE_RESULT"]
record = {"status": "FAIL", "mode": "OWN_SERVER_JOB", "port": int(os.environ["S2B_MANAGED_VITIS_PORT"]), "connect_called": False, "connected": False, "client_close_called": False, "dispose_called": False, "channel_closed": False, "sdk_owned_server_pid": None}
client = None
server_class = _server.Server
original_channel = server_class.channel
original_start_server = server_class.startServer
preconnected_channel = None
shim_installed = False
try:
    sdk_source_sha = hashlib.sha256(open(_server.__file__, "rb").read()).hexdigest()
    record["sdk_server_source"] = _server.__file__
    record["sdk_server_source_sha256"] = sdk_source_sha
    if sdk_source_sha != expected_sdk_sha or original_channel is not None or len(server_class._instances) != 0:
        raise RuntimeError("Vitis SDK源码或server singleton状态不满足受控shim前提")
    preconnected_channel = _server.grpc.insecure_channel("127.0.0.1:" + str(record["port"]))
    _server.grpc.channel_ready_future(preconnected_channel).result(10)
    server_class.channel = preconnected_channel
    def reject_sdk_server_start(instance):
        raise RuntimeError("managed server连接断开，禁止SDK创建非本Run server")
    server_class.startServer = reject_sdk_server_start
    shim_installed = True
    client = vitis.create_client(port=record["port"], host="127.0.0.1", workspace=os.environ["S2B_MANAGED_VITIS_WORKSPACE"])
    record["connect_called"] = True
    server = client._serverObj
    record["connected"] = server.verify() is True and server.serverPort == record["port"] and server.host == "127.0.0.1"
    record["sdk_owned_server_pid"] = None if server.cp is None else server.cp.pid
    if not record["connected"] or server.cp is not None:
        raise RuntimeError("连接未落到本Run外部server")
finally:
    if shim_installed:
        server_class.channel = original_channel
        server_class.startServer = original_start_server
    if preconnected_channel is not None:
        preconnected_channel.close()
    if client is not None:
        try:
            record["channel_closed"] = client.close() is True
            record["client_close_called"] = True
        except BaseException as error:
            record["client_close_error"] = repr(error)
    try:
        vitis.dispose()
        record["dispose_called"] = True
    except BaseException as error:
        record["dispose_error"] = repr(error)
    record["status"] = "PASS_SERVER_CLIENT_DISPOSE" if record["connected"] and record["client_close_called"] and record["dispose_called"] and record["channel_closed"] and record["sdk_owned_server_pid"] is None else "FAIL"
    with open(result_path, "x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
if record["status"] != "PASS_SERVER_CLIENT_DISPOSE":
    sys.exit(1)
