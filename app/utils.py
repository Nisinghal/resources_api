from app import API_VERSION
from flask import jsonify
import logging
import os


class Paginator:
    def __init__(self, configuration, request):
        self.configuration = configuration

        self.page = request.args.get('page', 1, type=int)
        self.page_size = request.args.get('page_size', configuration.per_page, type=int)

        if self.page_size > configuration.max_page_size:
            self.page_size = configuration.max_page_size

    def items(self, query):
        return query.paginate(self.page, self.page_size, False).items


def standardize_response(payload=None, status_code=200):
    """Response helper
    This simplifies the response creation process by providing an internally
    defined mapping of status codes to messages for errors. It also knows when
    to respond with a server error versus when to be 'ok' based on the keys
    present in the supplied payload.
    If the payload has falsey data and no error key defined, it responds with
    a 500.
    Arguments:
    payload -- None or a dict with 'data' or 'error' keys, 'data' should be
    json serializable
    status_code -- a valid HTTP status code. For errors it defaults to 500,
    for 'ok' it defaults to 200
    """
    if not payload:
        payload = {}
    data = payload.get("data")
    errors = payload.get("errors")
    resp = dict(
        apiVersion=API_VERSION,
        status="ok",
        status_code=status_code,
        data=None
    )

    err_map = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Unauthorized",
        404: "Not Found",
        422: "Unprocessable Entity",
        429: "Rate Limit Exceeded",
        500: "Server Error"
    }

    if status_code >= 400 and err_map.get(status_code):
        resp["status"] = err_map.get(status_code)
        resp["status_code"] = status_code

        if errors:
            resp["errors"] = errors
        else:
            resp["errors"] = [{
                "code": '-'.join(err_map.get(status_code).split(' ')).lower()
            }]

    elif not data:
        resp["errors"] = [{"code": "something-went-wrong"}]
        resp["status_code"] = 500
        resp["status"] = "error"
    else:
        resp["data"] = data

    return jsonify(resp), resp["status_code"], {'Content-Type': 'application/json'}


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    if not os.path.exists('log'):
        os.makedirs('log')

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
