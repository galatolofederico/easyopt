import os
import socket
import threading
import time

from easyopt.utils import recv_object, send_object

_easyopt_socket = None

def init_socket():
    global _easyopt_socket
    if _easyopt_socket is None and "EASYOPT_SOCKET" in os.environ:
        _easyopt_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        _easyopt_socket.connect(os.environ["EASYOPT_SOCKET"])


def init_heartbeat():
    if "EASYOPT_SOCKET" in os.environ:
        def heartbeat():
            init_socket()
            send_object(dict(command="heartbeat"), _easyopt_socket)
            time.sleep(5)

        _heartbeat_thread = threading.Thread(target=heartbeat)
        _heartbeat_thread.start()

def objective(value):
    if "EASYOPT_SOCKET" not in os.environ:
        return
    global _easyopt_socket
    init_socket()
    send_object(dict(command="objective", value=value), _easyopt_socket)

def report(value):
    if "EASYOPT_SOCKET" not in os.environ:
        return
    global _easyopt_socket
    init_socket()
    send_object(dict(command="report", value=value), _easyopt_socket)

def should_prune():
    if "EASYOPT_SOCKET" not in os.environ:
        return
    global _easyopt_socket
    init_socket()
    send_object(dict(command="should_prune"), _easyopt_socket)
    reply = recv_object(_easyopt_socket)
    return reply["reply"]