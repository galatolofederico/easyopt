import os
import json
import socket

_easyopt_socket = None

def init_socket():
    global _easyopt_socket
    if _easyopt_socket is None and "EASYOPT_SOCKET" in os.environ:
        _easyopt_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        _easyopt_socket.connect(os.environ["EASYOPT_SOCKET"])

def objective(value):
    if "EASYOPT_SOCKET" not in os.environ:
        return
    global _easyopt_socket
    init_socket()
    _easyopt_socket.send(json.dumps(dict(command="objective", value=value)).encode("utf-8"))