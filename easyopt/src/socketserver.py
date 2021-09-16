import socket
import threading

from easyopt.utils import send_object, recv_object

class SocketServer:
    def __init__(self, queue, socket_file):
        self.queue = queue
        self.socket_file = socket_file

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_file)

    def stop(self):
        self.server.close()
    
    def listen(self):
        thread = threading.Thread(target=self.listen_thread)
        thread.start()

    def listen_thread(self):
        self.server.listen(1)
        while True:
            self.socket, self.address = self.server.accept()
            thread = threading.Thread(target=self.client_thread)
            thread.start()
            thread.join()

    def client_thread(self):
        while True:
            data = recv_object(self.socket)
            self.queue.put(data)
            if "command" in data and data["command"] == "objective":
                break
        
    def send(self, data):
        send_object(data, self.socket)