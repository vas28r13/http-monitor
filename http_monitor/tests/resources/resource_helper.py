import http_monitor
import os

from pathlib import Path


TEST_HTTP_REQUEST_FILE = Path(os.path.dirname(http_monitor.tests.resources.__file__) + "/test_csv.txt")
