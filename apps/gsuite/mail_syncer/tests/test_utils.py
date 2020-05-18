from googleapiclient.errors import HttpError
from httplib2 import Response


def create_http_response(status, reason):
    resp = Response({"status": status})
    resp.reason = reason
    return resp


def create_http_error(status, reason, error):
    return HttpError(
        resp=create_http_response(status, reason),
        content=bytes(('{"error": {"message": "%s"}}' % error).encode("UTF-8")),
    )
