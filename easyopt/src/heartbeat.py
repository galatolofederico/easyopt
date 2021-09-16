import threading
import time

from easyopt.utils import send_object, log

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
        log(f"[heartbeat] beat")
        self.last_heartbeat = time.time()

    def stop(self):
        log(f"[heartbeat] stopped")
        self.running = False

    def heartbeat(self):
        while self.running:
            delta = time.time() - self.last_heartbeat
            log(f"[heartbeat] delta: {delta}")
            if delta > self.sleep_time and self.running:
                log(f"[heartbeat] sending heartbeat_fail")
                self.queue.put(dict(command="heartbeat_fail"))
            time.sleep(self.sleep_time)