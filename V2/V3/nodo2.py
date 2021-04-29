
import time
import zmq
import threading as th

nodos_adyacentes = ["5555","5556","5557"]
#nodos_adyacentes = ["5555","5556","5558"]
#nodos_adyacentes = ["5555","5557","5558"]
#nodos_adyacentes = ["5556","5557","5558"]

def server():
    print ("server")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5556")
    message = socket.recv()
    print("Received request: %s" % message)
    #  Send reply back to client
    socket.send(b"World")

def client():
    print ("client")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    print("Sending request %s …" % 5)
    socket.send(b"Hello desde 5556")
    message = socket.recv()
    print("Received reply %s [ %s ]" % (1, message))

input("¿Empezar?")

nodo_s = th.Thread(target=server)
#  Socket to talk to server
#print("Connecting to hello world server…")
nodo_c = th.Thread(target=client)

nodo_s.start()
nodo_c.start()