"""
    It provides a way to pipe a float32 stream to GNU Radio
    For measurements and debug
"""
import zmq

class ZMQSend():
    def __init__(self, port=5555):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)

    def send(self, data):
        null = self.socket.recv()
        self.socket.send(data)
