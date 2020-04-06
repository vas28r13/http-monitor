FROM python:3.7-slim

RUN mkdir -p /opt/scripts/
WORKDIR /opt/scripts/

COPY ./requirements.txt /opt/scripts/

RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir --requirement requirements.txt

CMD python3.7 run_http_monitor.py