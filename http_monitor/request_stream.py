import logging
import os

from http_monitor.request import Request


class Stream:

    HTTP_METHODS = ["GET", "HEAD", "POST", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]

    def __init__(self, file_path):
        self.file_path = file_path
        self.filehandler = open(file_path, 'r')
        self.inode = os.fstat(self.filehandler.fileno()).st_ino

    def get_request(self):
        where = self.filehandler.tell()
        # TODO: add option to read chunks of lines instead of 1 at a time
        raw_request = self.filehandler.readline()
        if raw_request:
            return self._parse_request(raw_request.strip())
        else:
            file_inode = os.stat(self.file_path).st_ino
            if file_inode != self.inode:
                # file inode was updated, either log rotation or appending requests manually using some IDE
                self.inode = file_inode
                self.filehandler = open(self.file_path, 'r')
                self.filehandler.seek(where)
            return None

    def _parse_request(self, raw_request):
        try:
            raw_request = raw_request.split(',')
            self._parse_http_request(raw_request[4])
            method, resource, path, http_version = self._parse_http_request(raw_request[4])
            request = Request(
                remotehost=raw_request[0]
                , rfc931=raw_request[1]
                , authuser=raw_request[2]
                , date=int(raw_request[3])
                , status=str(raw_request[5])
                , bytes=int(raw_request[6])
                , method=method
                , resource=resource
                , path=path
                , http_version=http_version
            )
            return request
        except Exception as e:
            # TODO: handle the case for the csv header more gracefully
            logging.error(f'could not parse raw request={raw_request}, exception={e}')
            return None

    def _parse_http_request(self, raw_http_request):
        """
        parsing: "GET /api/user HTTP/1.0"
        return: GET, api, /api/user, HTTP/1.0
        """
        http_request = raw_http_request.strip('\"').split()
        if http_request[0] not in self.HTTP_METHODS or http_request[2][:4] != "HTTP":
            raise ValueError(f'{raw_http_request} is not a valid http request!')
        resource = http_request[1].split('/')[1]
        return http_request[0], resource, http_request[1], http_request[2]
