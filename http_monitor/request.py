import attr


@attr.s(frozen=True)
class Request:
    remotehost = attr.ib()
    rfc931 = attr.ib()
    authuser = attr.ib()
    date = attr.ib()
    status = attr.ib()
    bytes = attr.ib()
    method = attr.ib()
    resource = attr.ib()
    path = attr.ib()
    http_version = attr.ib()

