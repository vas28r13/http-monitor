import argparse
import logging
import pathlib
import yaml

from http_monitor.monitor import Monitor
from pathlib import Path

logging.getLogger().setLevel(logging.INFO)

REQUESTS_FILE = pathlib.Path.cwd().joinpath(Path('sample_csv.txt'))
DEFAULT_CONFIG = pathlib.Path.cwd().joinpath(Path('config.yaml'))

if __name__ == "__main__":
    with open(DEFAULT_CONFIG, "r") as ymlfile:
        config = yaml.safe_load(ymlfile)
        monitor_settings = config['monitor_settings']
        refresh_rate = monitor_settings['refresh_rate']
        alert_threshold = monitor_settings['avg_hits_alert_threshold']

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, default=REQUESTS_FILE)
    args = parser.parse_args()

    monitor = Monitor(args.file, refresh_rate, alert_threshold)
    monitor.start_monitor()
