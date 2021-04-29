
import time
import zmq
import threading as th
import json
import queue as q

nodos_adyacentes = ["5555","5556","5557"]
#nodos_adyacentes = ["5556","5555","5558"]
#nodos_adyacentes = ["5557","5555","5558"]
#nodos_adyacentes = ["5558","5556","5557"]

global state
global voted
global pendient_queue
global n_respuestas
global respuesta

state = "released"
voted = False
pendient_queue = []
n_respuestas = 0

def recibirRespuesta(socket):
    message = socket.recv_json()
    print("Respuesta recibida:",message)
    return message

def enviarRespuesta(socket,message):
    print("Respuesta que se envia es: ",message)
    socket.send_json(message)
    
def valorarRespuesta(socket,message):
    global voted
    global n_respuestas
    if(message["solicitud"]=="request"):
        if(state=="held" or voted==True):
            if(message["id"] not in pendient_queue):
                pendient_queue.append(message["id"])
                print(pendient_queue)
                print("se encola")
            return    {
                "solicitud":"failed",
                "id":message["id"]
            }
        else:
            #voted = True
            print("entra en request")
            return {
                "solicitud":"accepted",
                "id":message["id"]
            }
            
    if(message["solicitud"]=="released"):
        print("entra con released")
        if pendient_queue:
            voted = True
            return{
                "solicitud":"accepted",
                "id":message["id"]
                }
        else:
            voted = False
    
    if(message["solicitud"]=="accepted"):
        print("suma respuestas")
        n_respuestas = n_respuestas + 1

def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:"+nodos_adyacentes[0])
    
    while True:
        #  Wait for next request from client
        message = recibirRespuesta(socket)
        print("Received request: %s %s" % (message,nodos_adyacentes[0]))
        #  Do some 'work'
        time.sleep(1)
        #  Send reply back to client
        message_1 = valorarRespuesta(socket, message)
        socket.send_json(message_1)

        if(message_1["solicitud"] == "accepted"):
            #  Wait for next request from client
            message = recibirRespuesta(socket)
            print("Received request: %s %s" % (message,nodos_adyacentes[0]))
            #  Do some 'work'
            time.sleep(1)
            #  Send reply back to client
            message_1 = valorarRespuesta(socket, message)
            socket.send_json(message_1)

def preguntar_zona_critica():
    global respuesta
    #global nodo_c_1
    #global nodo_c_2
    while True:
        respuesta = bool(int(input("desea entrar: ")))
        if (respuesta):
            nodo_c_1 = th.Thread(target=client_1)
            nodo_c_1.start()
            time.sleep(1)
            nodo_c_2 = th.Thread(target=client_2)
            nodo_c_2.start()
            time.sleep(1)
            nodo_c_3 = th.Thread(target=client_3)
            nodo_c_3.start()
            time.sleep(10)



def client_1():
    global state
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[0])
    #  Do 10 requests, waiting each time for a response
    state = "wanted"
    message = {
        "solicitud":"request",
        "id":nodos_adyacentes[0]
    }
    print("Sending request %s %s…" % ("client_1", nodos_adyacentes[0]))
    socket.send_json(message)
    #  Get the reply.
    message = socket.recv_json()
    if(message["id"]==nodos_adyacentes[0] and message["solicitud"]=="accepted"):
        print("aceptado")
        print("Received reply %s [ %s ]" % ("client_1", message))
        message = {
            "solicitud":"released",
           "id":nodos_adyacentes[0]
        }
        socket.send_json(message)
        socket.recv_json()

def client_2():
    global state
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[0])
    #  Do 10 requests, waiting each time for a response
    while (bool(int(input("desea entrar: ")))):
        state = "wanted"
        message = {
            "solicitud":"request",
            "id":nodos_adyacentes[1]
        }
       
        print("Sending request %s %s…" % ("client_2", nodos_adyacentes[1]))
        socket.send_json(message)
        #  Get the reply.
        message = socket.recv_json()
        if(message["id"]==nodos_adyacentes[1] and message["solicitud"]=="accepted"):
            print("aceptado")
            print("Received reply %s [ %s ]" % ("client_2", message))
            message = {
                "solicitud":"released",
               "id":nodos_adyacentes[1]
            }
            socket.send_json(message)
            socket.recv_json()

def client_3():
    global state
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[0])
    #  Do 10 requests, waiting each time for a response
    while (bool(int(input("desea entrar: ")))):
        state = "wanted"
        message = {
            "solicitud":"request",
            "id":nodos_adyacentes[2]
        }
       
        print("Sending request %s %s…" % ("client_3", nodos_adyacentes[2]))
        socket.send_json(message)
        #  Get the reply.
        message = socket.recv_json()
        if(message["id"]==nodos_adyacentes[2] and message["solicitud"]=="accepted"):
            print("aceptado")
            print("Received reply %s [ %s ]" % ("client_3", message))
            message = {
                "solicitud":"released",
               "id":nodos_adyacentes[2]
            }
            socket.send_json(message)
            socket.recv_json()


nodo_s = th.Thread(target=server)
nodo_s.start()
#zona_critica = th.Thread(target=preguntar_zona_critica)
#nodo_c_1 = th.Thread(target=client_1)
preguntar_zona_critica()
#zona_critica.start()
#nodo_c_1.start()
#time.sleep(10)
#nodo_c_2 = th.Thread(target=client_2)
#nodo_c_2.start()
#nodo_c_3 = th.Thread(target=client_3)