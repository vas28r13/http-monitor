# http-monitor
simple console utility to monitor a http requests from a requests log file

## runbook

### docker container
```bash
docker-compose up
```
Note: appending to the request log file outside the container when running in the docker container will not stream the new data

### python env
```bash
pip install requirements.txt
python3.7 run_http_monitor.py
or
python3.7 run_http_monitor.py --file {path_to_requests_log_file}
```
Appending to request log file should stream monitor metrics

### tests
```bash
pytest
```

## Configs
monitor configurations live here:
`./config.yaml`

* `refresh_rate`: time window (in seconds) to aggregate metrics around the stream of http request logs (i.e. every 10 seconds show stats that happened in that 10second interval) 
* `avg_hits_alert_threshold`: whenever the average number of requests (per second) goes over this threshold we throw an alert

## Assumptions
* Assuming that timestamped request logs are more or less in order of the request timestamps. Some sample logs are not in order but are very close, which may slightly skew some metrics. This implementation does not resort the request based on the request timestamp so metrics may get skewed if for some reason requests are written to the log out of order.
* Assuming that there aren't large time gaps between requests logs. This implemetation should still work for this case but will be noisy since it will print out metrics for every 10sec interval  between the 2 log timestamps.
 

## Things to consider
* only handles csv format at the moment
* Refresh rate intervals for keeping track of http request metrics are defined in this object: `interval.py`
* the program essentially streams the http request logs from the file and buckets them to the approriate `interval`
* 10-second intervals start at the timestamp of the first request
* `interval` does not try to validate that the request log timestamp happens after the start of the interval but does try to validate that the request happened before the end of the interval. Therefore, this will not do well if old request logs begin streaming into the file
* This implementation should catch up to the tail of the request log and begin monitoring the current time.
* there is a bit of an ambigious transition between catching metrics up to the current time and beginning live monitoring of tailed logs
* if there is no more http request logs in the file then the monitor begins to live monitor, which means that it will skip over to the current timestamp interval and start the 10-seconds interval from "now" on
* appending new request log data to the file should display new metrics
* manually appending new request log data to the log file in pycharm changes the inode of the file (inode switch is handled in `request_stream.py`)
* for the Alert, this implementation checks the last 120 seconds of published metrics `intervals`, which I think makes it simpler but unfortunately means that the alert may be delayed by several seconds.

## Needed improvements
* the http requests Alert is coupled with the `refresh_rate` of the http request metrics `interval`. This means that there may be a delay of several seconds before an alert is dispatched (depends on the `refresh_rate` settings). At this point, only checking the alert state at the time of publishing the metrics `interval`. Could improve the granularity of the alert by using a separate queue to maintain the last 120seconds of requests.
* if data is deleted in the request log while it's streaming then the position of the log stream gets messed up so there may be some duplicate request metrics
* there is a bit of an ambigious transition between catching metrics up to the current time and beginning live monitoring of tailed logs
* gracefully handle parsing the csv header
* more tests and documentation
* current tests are not sufficient to prove confidence in this implementation
* when in live logging mode (tailing log file), the metrics intervals won't perfectly align when there is a series of 0 requests during the intervals. (Tries to catch up the interval to the current time when there are no requests). This should be fine for the purposes of monitoring but would make things a bit tricky if we were to persist these metrics and later try to graph them up. 