import collections
import logging
import pendulum
import time

from http_monitor.interval import Interval
from http_monitor.request_buffer import RequestBuffer


class Monitor:
    """
    monitors statistics for metrics intervals for a stream of http requests
    also responsible for setting alert state
    """
    def __init__(self
                 , request_file_path
                 , refresh_rate
                 , avg_hits_threshold
                 , poll_delay=1.0
                 , alert_window=120
                 , is_live_monitor=True
                 ):
        """
        :param request_file_path: the http request file to monitor
        :param refresh_rate: the time interval to aggregate metrics around
        :param avg_hits_threshold: alert threshold for avg requests per second
        :param poll_delay: poll delay for empty request buffer
        :param alert_window: look back seconds to monitor alerts
        :param is_live_monitor: whether to keep tailing file and monitoring or stop once all requests are read
        """
        self.request_file_path = request_file_path
        self.refresh_rate = refresh_rate
        self.avg_hits_threshold = avg_hits_threshold
        self.poll_delay = poll_delay
        self.alert_window = alert_window
        self.alert_state = False
        self.latest_alert_timestamp = 0
        self.interval_queue = collections.deque()
        self.is_live_monitor = is_live_monitor

    def start_monitor(self):
        request_buffer = RequestBuffer(self.request_file_path)
        request_buffer.start()
        current_interval = None
        while True:
            # TODO: clean this up, break this up! too many if else if else if else
            if request_buffer.request_queue.empty():
                now = int(time.time())
                if current_interval and now > current_interval.end_ts:
                    prev_end_ts = current_interval.end_ts
                    prev_hits = current_interval.hits
                    self._process_metrics_interval(current_interval)
                    # start live monitoring at current time if there is no more requests to bucket
                    if prev_hits == 0:
                        if self.is_live_monitor:
                            current_interval = Interval(now, self.refresh_rate)
                        else:
                            logging.info("All http request logs processed! Not in live monitoring mode so we're done!")
                            request_buffer.stop()
                            return
                    else:
                        current_interval = Interval(prev_end_ts, self.refresh_rate)
                time.sleep(self.poll_delay)
            else:
                request = request_buffer.request_queue.get()
                if current_interval is None:
                    # metrics interval starts with the timestamp of the first request
                    current_interval = Interval(request.date, self.refresh_rate)
                while not current_interval.process_request(request):
                    prev_end_ts = current_interval.end_ts
                    self._process_metrics_interval(current_interval)
                    current_interval = Interval(prev_end_ts, self.refresh_rate)

    def _process_metrics_interval(self, interval):
        """
        this method wraps up a completed metrics interval and really does too much:
        1. append to the interval_queue to keep track to be able to able to looks back numerous data points
        2. display the metrics around this interval
        3. check if there is any alerts in the last 120 seconds of metric intervals
        """
        self.interval_queue.append(interval)
        # display some stats
        interval.display_stats()

        alert_window_hits = sum([i.hits for i in self.interval_queue])
        alert_dt = pendulum.from_timestamp(interval.end_ts)

        if (alert_window_hits / self.alert_window) > self.avg_hits_threshold:
            self._set_alert(True, alert_dt, alert_window_hits)
        else:
            self._set_alert(False, alert_dt, alert_window_hits)

        # popping off older intervals beyond the alert window to clean up
        num_intervals_lookback = int(self.alert_window / self.refresh_rate)
        if len(self.interval_queue) == num_intervals_lookback:
            self.interval_queue.popleft()

    def _set_alert(self, is_alert_state, alert_dt, alert_window_hits):
        """
        sets monitor alert state
        """
        if self.alert_state == is_alert_state:
            return
        elif self.alert_state is True and is_alert_state is False:
            logging.critical(
                f'Woohoo high traffic alert recovered - hits = {alert_window_hits}, recovered at time={alert_dt}'
            )
            self.alert_state = False
        elif self.alert_state is False and is_alert_state is True:
            logging.critical(
                f'High traffic generated an alert - hits = {alert_window_hits}, triggered at time={alert_dt}'
            )
            self.alert_state = True
            self.latest_alert_timestamp = alert_dt.int_timestamp
