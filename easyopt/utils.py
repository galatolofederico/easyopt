import json
import os

def log(msg):
    if "EASYOPT_DEBUG" in os.environ:
        print(msg)

def recv_until_newline(socket):
    ret = ""
    char = ""
    while char != "\n":
        char = socket.recv(1).decode("utf-8")
        ret += char
    return ret

def recv_object(socket):
    datagram = recv_until_newline(socket).rstrip()
    return json.loads(datagram)

def send_object(obj, socket):
    socket.send((json.dumps(obj)+"\n").encode("utf-8"))