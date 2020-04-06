import pytest

from http_monitor.monitor import Monitor
from http_monitor.tests.resources.resource_helper import TEST_HTTP_REQUEST_FILE


@pytest.fixture
def alerting_monitor():
    return Monitor(TEST_HTTP_REQUEST_FILE, 10, 1, 0.1, 120, False)


@pytest.fixture
def non_alerting_monitor():
    return Monitor(TEST_HTTP_REQUEST_FILE, 10, 1.1, 0.1, 120, False)


def test_alert_dispatch(alerting_monitor):
    alerting_monitor.start_monitor()
    assert alerting_monitor.alert_state
    assert 1549573870 == alerting_monitor.latest_alert_timestamp


def test_no_alert_dispatch(non_alerting_monitor):
    non_alerting_monitor.start_monitor()
    assert not non_alerting_monitor.alert_state
    assert 0 == non_alerting_monitor.latest_alert_timestamp
