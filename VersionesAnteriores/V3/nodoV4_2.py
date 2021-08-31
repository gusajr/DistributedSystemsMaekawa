
import time
import zmq
import threading as th
import json
import queue as q

#nodos_adyacentes = ["5555","5556","5557"]
nodos_adyacentes = ["5556","5555","5558"]
#nodos_adyacentes = ["5557","5555","5558"]
#nodos_adyacentes = ["5558","5556","5557"]

global state
global voted
global pendient_queue
global n_respuestas
global opcion

state = "released"
voted = False
pendient_queue = []
n_respuestas = 0
opcion = False

def getInput():
    global opcion
    while True:
        opcion = bool(int(input("¿desea entrar a la zona crítica? 0.No, 1.Si: ")))
    
def recibirRespuesta(socket):
    message = socket.recv_json()
    print("Respuesta recibida:",message)
    return message

def enviarRespuesta(socket,message):
    socket.send_json(message)
    
def valorarRespuesta(socket,message):
    global voted
    global n_respuestas
    global nodos_adyacentes
    if(message["solicitud"]=="request"):
        if(state=="held" or voted==True):
            if(message["id"] not in pendient_queue):
                pendient_queue.append(message["id"])
                print(pendient_queue)
                print("se encola")
            socket.send_json    ({
                "solicitud":"failed",
                "id":nodos_adyacentes[0]
            })
        else:
            voted = True
            socket.send_json({
                "solicitud":"accepted",
                "id":nodos_adyacentes[0]
            })
            
    if(message["solicitud"]=="released"):
        print("entra con released")
        if pendient_queue:
            socket.connect("tcp://localhost:"+pendient_queue.pop(0))
            socket.send(
                {
                "solicitud":"accepted",
                "id":nodos_adyacentes[0]
                }
            )
            voted = True
        else:
            voted = False
    
    if(message["solicitud"]=="accepted"):
        print("suma respuestas")
        n_respuestas = n_respuestas + 1

def server():
    global nodos_adyacentes
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:"+nodos_adyacentes[0])
    while True:
        enviarRespuesta(socket,valorarRespuesta(socket,recibirRespuesta(socket)))
        time.sleep(1)

def client():
    global state
    global voted
    global n_respuestas
    global nodos_adyacentes
    global opcion
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    inputThread = th.Thread(target=getInput)
    inputThread.start()
    while True:
        if(opcion): 
            state = "wanted"
            message = {
                "solicitud":"request",
                "id":nodos_adyacentes[0]
                }
            
            client_1(socket,message,nodos_adyacentes[0])
            client_1(socket,message,nodos_adyacentes[1])
            client_1(socket,message,nodos_adyacentes[2])

            while True:
                time.sleep(1)
                if (n_respuestas >= 1):
                    break

            state = "held"
            print("aceptado")
            message = {
                "solicitud":"released",
               "id":nodos_adyacentes[0]
            }
            #print(n_respuestas)
            #print("llega hasta aqui")

            client_1(socket,message,nodos_adyacentes[0])
            client_1(socket,message,nodos_adyacentes[1])
            client_1(socket,message,nodos_adyacentes[2])

            #state = "released"
            #print("se aviso a los demás:",state,voted)
            n_respuestas = 0

def client_1(socket, message, nodo_adyacente):
    socket.connect("tcp://localhost:"+nodo_adyacente)
    enviarRespuesta(socket,message)
    message = recibirRespuesta(socket)
    if(message != None):
        valorarRespuesta(socket,message)
    #valorarRespuesta(socket, message)

nodo_s = th.Thread(target=server)
nodo_c = th.Thread(target=client)

nodo_s.start()
nodo_c.start()