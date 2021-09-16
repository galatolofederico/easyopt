import os
import socket
import threading
import time

from easyopt.utils import recv_object, send_object, log

_easyopt_socket = None

_easyopt_socket_lock = threading.Lock()
_easyopt_heartbeat_lock = threading.Lock()

_heartbeat_thread = None
_heartbeat_thread_running = True

def init():
    init_heartbeat()

def init_socket():
    global _easyopt_socket
    global _easyopt_socket_lock
    with _easyopt_socket_lock:
        if _easyopt_socket is None and "EASYOPT_SOCKET" in os.environ:
            log("[lib] initializing socket")
            _easyopt_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            _easyopt_socket.connect(os.environ["EASYOPT_SOCKET"])


def init_heartbeat():
    if "EASYOPT_SOCKET" in os.environ:
        def heartbeat():
            global _heartbeat_thread_running
            while _heartbeat_thread_running:
                init_socket()
                time.sleep(1)
                log(f"[lib] sending hearbeat _heartbeat_thread_running={_heartbeat_thread_running}")
                send_object(dict(command="heartbeat"), _easyopt_socket)
            log("[lib] heartbeat_thread terminated")
            return

        global _heartbeat_thread
        global _easyopt_heartbeat_lock
        with _easyopt_heartbeat_lock:
            if _heartbeat_thread is None:
                _heartbeat_thread = threading.Thread(target=heartbeat)
                _heartbeat_thread.start()
                log("[lib] heartbeat_thread started")

def objective(value):
    if "EASYOPT_SOCKET" not in os.environ:
        return
    global _easyopt_socket
    global _heartbeat_thread_running

    init_socket()
    send_object(dict(command="objective", value=value), _easyopt_socket)
    _heartbeat_thread_running = False
    _heartbeat_thread.join()
    log("[lib] heartbeat_thread joined")

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