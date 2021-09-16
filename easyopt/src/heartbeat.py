import threading
import time

from easyopt.utils import send_object

class HeartbeatException(Exception):
    pass

class HeartbeatMonitor:
    def __init__(self, queue, sleep_time=10):
        self.queue = queue
        self.sleep_time = sleep_time
        self.running = True
        self.beat()
        
        self.heartbeat_thread = threading.Thread(target=self.heartbeat, )
        self.heartbeat_thread.start()

    def beat(self):
        self.last_heartbeat = time.time()

    def stop(self):
        self.running = False

    def heartbeat(self):
        while self.running:
            delta = time.time() - self.last_heartbeat
            if delta > self.sleep_time and self.running:
                self.queue.put(dict(command="heartbeat_fail"))
            time.sleep(self.sleep_time)