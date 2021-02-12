"""
    It provides a way to pipe a float32 stream to GNU Radio
    For measurements and addons
"""
import zmq
import os
import numpy as np


class ZMQSend:
    def __init__(self, port=5555):
        self.pid = os.getpid()
        print('Initializing ZMQSend (REP) at pid %d, port %d' % (self.pid, port))
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)

    def chekcpid(self):
        assert os.getpid() == self.pid, \
            "You cannot call send from another thread: expected %d found %d" % (self.pid, pid)

    def send(self, data):
        self.chekcpid()
        null = self.socket.recv()
        self.socket.send(data.astype(np.float32))

    def send_complex(self, complex):
        self.chekcpid()
        null = self.socket.recv()
        data = np.empty((complex.real.size + complex.imag.size,), dtype=np.float32)
        data[0::2] = complex.real.astype(np.float32)
        data[1::2] = complex.imag.astype(np.float32)
        #print('go!', complex.real, complex.imag, data)
        self.socket.send(data)


class ZMQReceive:
    def __init__(self, port=5555):
        self.pid = os.getpid()
        print('Initializing ZMQReceive (REQ) at pid %d, port %d' % (self.pid, port))
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % port)

    def chekcpid(self):
        assert os.getpid() == self.pid, \
            "You cannot call send from another thread: expected %d found %d" % (self.pid, pid)

    def receive(self):
        self.chekcpid()
        self.socket.send_string("hello")
        return self.socket.recv()
