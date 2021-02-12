#!/usr/bin/env python3
import sys
sys.path.insert(1, '../../')

from vhsdecode.addons.zmq_grc import ZMQReceive

pipe = ZMQReceive()
while True:
    print(pipe.receive())
