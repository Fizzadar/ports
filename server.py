#!/usr/bin/env python

# Ports
# File: server.py
# Desc: port checker

# Async everything
from gevent import monkey
monkey.patch_all()

from socket import socket, error as socket_error

from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify

import settings


app = Flask('ports')
app.debug = settings.DEBUG


def _get_remote_addr():
    remote_addr = request.headers.getlist('X-Real-IP')
    if remote_addr:
        remote_addr = remote_addr[0]
    else:
        remote_addr = request.remote_addr

    return remote_addr


@app.route('/')
def index():
    remote_addr = _get_remote_addr()

    return jsonify(host=remote_addr)


@app.route('/<int:port_number>')
def check_port(port_number):
    remote_addr = _get_remote_addr()

    data = {
        'host': remote_addr,
        'port': port_number
    }

    sock = socket()
    sock.settimeout(settings.TIMEOUT)

    try:
        sock.connect((remote_addr, port_number))
        data['open'] = True
    except socket_error as e:
        data['error'] = e.strerror
        data['open'] = False

    return jsonify(**data)


if __name__ == '__main__':
    http = WSGIServer((settings.HOST, settings.PORT), app)
    http.serve_forever()
