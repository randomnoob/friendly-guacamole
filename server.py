# DB updater

#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
from mult import Storage
import json
from mongoengine import *

class Result(Document):
    kw = StringField(required=True)
    result = StringField(required=True)

    def __repr__(self):
        return self.kw
    def __str__(self):
        return self.kw

context = zmq.Context()
storage = Storage()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    data = json.loads(message)
    print("Received request: %s" % data.get('kw'))

    #  Do some 'work'
    Result(kw=data.get('kw'), result=data.get('result')).save()
    storage.change_status(message)

    #  Send reply back to client
    # socket.send(b"Success")
