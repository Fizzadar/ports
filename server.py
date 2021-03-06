#!/usr/bin/env python

# Ports
# File: server.py
# Desc: port checker

# Async everything
from gevent import monkey
monkey.patch_all()

import socket

from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify

import settings_default

try:
    import settings
except ImportError:
    settings = settings_default

# Set any missing default settings
for attr in [attr for attr in dir(settings_default) if attr.isupper()]:
    if not hasattr(settings, attr):
        setattr(settings, attr, getattr(settings_default, attr))


app = Flask('ports')
app.debug = settings.DEBUG


def _get_remote_addr():
    remote_addr = request.headers.getlist('X-Real-IP')
    if remote_addr:
        remote_addr = remote_addr[0]
    else:
        remote_addr = request.remote_addr

    return remote_addr


@app.before_request
def secret_check():
    if settings.SECRET:
        if request.args.get('secret') != settings.SECRET:
            return jsonify(error='Invalid secret, add ?secret')


@app.route('/')
def index():
    remote_addr = _get_remote_addr()

    return jsonify(host=remote_addr, usage='/<port_number>')


@app.route('/<int:port_number>')
def check_port(port_number):
    remote_addr = _get_remote_addr()

    data = {
        'host': remote_addr,
        'port': port_number
    }

    sock = socket.socket()
    sock.settimeout(settings.TIMEOUT)

    is_open = False

    try:
        sock.connect((remote_addr, port_number))
        is_open = True
    except socket.timeout:
        data['error'] = 'Timed out'
    except socket.error as e:
        data['error'] = e.strerror

    data['open'] = is_open

    return jsonify(**data)


if __name__ == '__main__':
    http = WSGIServer((settings.HOST, settings.PORT), app)
    http.serve_forever()
