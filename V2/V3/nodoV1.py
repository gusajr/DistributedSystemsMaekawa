
import time
import zmq
import threading as th
import json

nodos_adyacentes = ["5555","5556","5557"]
#nodos_adyacentes = ["5555","5556","5558"]
#nodos_adyacentes = ["5555","5557","5558"]
#nodos_adyacentes = ["5556","5557","5558"]

global state
global voted

state = "released"
voted = "false"

def recibirRespuesta(socket):
    message = socket.recv_json()#.decode("utf-8")
    return message

def enviarRespuesta(socket):
    y = ("respuesta","id:550")
    socket.send_json(json.dumps(y))#.encode('utf-8'))
    

def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    while True:
        recibirRespuesta(socket)
        enviarRespuesta(socket)
        ##message = socket.recv().decode("utf-8")
        ##print("Received request: %s" % message)
        ##socket.send(message.encode('utf-8'))
        #if(message=="salir"):
        #    break

def client():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    while True:
        #print("Sending request %s …" % 5)
        if(bool(int(input("¿desea entrar a la zona crítica? 0.No, 1.Si: ")))):
            #ENVIAR A TODOS REQUEST
            #van a ser 6 hilos por programa
            enviarRespuesta(socket)
            message = recibirRespuesta(socket)
            print(message)
            ##socket.send(str(input()).encode('utf-8'))
            ##message = socket.recv().decode('utf-8')
        #if(message=="salir"):
        #    break
        #print("Received reply %s [ %s ]" % (1, message))

time.sleep(3)

nodo_s = th.Thread(target=server)
nodo_c = th.Thread(target=client)

nodo_s.start()
nodo_c.start()