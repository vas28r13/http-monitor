import logging
import pendulum


class Interval:
    """
    represents a metrics data point around an time window interval of http requests
    """

    def __init__(self, start_ts, seconds_interval):
        self.start_ts = start_ts
        self.end_ts = start_ts + seconds_interval
        self.hits = 0
        self.status_counts = dict()
        self.resource_counts = dict()

    def process_request(self, request):
        if request.date > self.end_ts:
            return False

        self.hits += 1
        self.status_counts[request.status] = self.status_counts.get(request.status, 0) + 1
        self.resource_counts[request.resource] = self.resource_counts.get(request.resource, 0) + 1
        return True

    def display_stats(self):
        start_dt = pendulum.from_timestamp(self.start_ts)
        end_dt = pendulum.from_timestamp(self.end_ts)

        logging.info(
            f'[{start_dt} - {end_dt}]'
            f' hits={self.hits}'
            f', status_counts={self.status_counts}'
            f', resource_counts={self.resource_counts}'
            f', most hits section={self._get_most_hits_section()}'
        )

    def _get_most_hits_section(self):
        most_hits_section = None
        max_val = 0
        for key, value in self.resource_counts.items():
            if value > max_val:
                most_hits_section = key
                max_val = value
        return most_hits_section
