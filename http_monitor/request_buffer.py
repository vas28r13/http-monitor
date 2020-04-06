import queue
import threading
import time

from http_monitor.request_stream import Stream


class RequestBuffer(threading.Thread):
    """
    buffers a stream of http request logs
    """

    DEFAULT_BUFFER_SIZE = 10000
    DEFAULT_POLL_DELAY = 0.1

    def __init__(self, file_path, buffer_size=DEFAULT_BUFFER_SIZE, poll_delay=DEFAULT_POLL_DELAY):
        self.file_path = file_path
        self.stream = Stream(file_path)
        self.buffer_size = buffer_size
        self.poll_delay = poll_delay
        self.request_queue = queue.Queue()
        self._stop_event = False
        threading.Thread.__init__(self)

    def run(self):
        while not self._stop_event:
            # python io can probably handle buffering better
            # TODO: consider using a priority queue if the requests are written out of order a lot
            if not self.request_queue.qsize() > self.buffer_size:
                request = self.stream.get_request()
                if request:
                    self.request_queue.put(request)
                else:
                    time.sleep(self.poll_delay)
            else:
                time.sleep(self.poll_delay)

    def stop(self):
        self._stop_event = True
