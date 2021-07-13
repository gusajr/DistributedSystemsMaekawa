
import time
import zmq
import threading as th
import json
import queue as q
import datetime

nodos_adyacentes = ["5555","5556","5557"]
#nodos_adyacentes = ["5556","5555","5558"]
#nodos_adyacentes = ["5557","5555","5558"]
#nodos_adyacentes = ["5558","5556","5557"]

#archivo que modificarán los procesos
archivo = open("procesos.txt","w")
archivo.close()

global state
global voted
global pendient_queue
global n_respuestas
global respuesta

#estado inicial
state = "released"
voted = False
pendient_queue = []
n_respuestas = 0

#función para recibir una respuesta
def recibirRespuesta(socket):
    message = socket.recv_json()
    print("Respuesta recibida:",message)
    return message

#función para enviar una respuesta
def enviarRespuesta(socket,message):
    print("Respuesta que se envia es: ",message)
    socket.send_json(message)
    
#función para determinar qué respuesta se recibió
def valorarRespuesta(socket,message):
    global voted
    global n_respuestas
    if(message["solicitud"]=="request"):
        if(state=="held" or voted==True):
            if(message["id"] not in pendient_queue):
                pendient_queue.append(message["id"])
                print(pendient_queue)
                print("se encola proceso con id:", message["id"])
                return    {
                    "solicitud":"failed",
                    "id":message["id"]
                }
        else:
            voted = True
            print("entra en request")
            return {
                "solicitud":"accepted",
                "id":message["id"]
            }
            
    if(message["solicitud"]=="released"):
        print("entra con released")
        if pendient_queue:
            print("entra en pendiente")
            voted = True
            return{
                "solicitud":"accepted",
                "id":pendient_queue.pop(0)
                }
        else:
            voted = False
            return{
                "solicitud":"accepted",
                "id":message["id"]
            }

#función del servidor, siempre recibiendo respuestas
def server():
    global n_respuestas
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:"+nodos_adyacentes[0])
    
    while True:
        #se espera a una solicitud desde algún cliente
        message = recibirRespuesta(socket)
        print("Se recibe solicitud de: %s %s" % (message,message["id"]))
        time.sleep(1)
        #se envia respuesta al cliente
        print("Valorando respuesta en servidor...")
        message_1 = valorarRespuesta(socket, message)
        socket.send_json(message_1)
        print("mensaje_1: ", message_1)
        if(message_1["solicitud"]=="accepted" and message_1["id"]==nodos_adyacentes[0]):
            n_respuestas = n_respuestas + 2

#función para preguntar si se entra a la sección crítica y lo que hace allí
def preguntar_seccion_critica():
    global respuesta
    global n_respuestas
    global state
    #global nodo_c_1
    #global nodo_c_2
    while True:
        respuesta = bool(int(input("desea entrar: ")))
        if (respuesta):
            state = "wanted"
            nodo_c_1 = th.Thread(target=client_1)
            nodo_c_1.start()
            time.sleep(1)
            nodo_c_2 = th.Thread(target=client_2)
            nodo_c_2.start()
            time.sleep(1)
            nodo_c_3 = th.Thread(target=client_3)
            nodo_c_3.start()
            time.sleep(10)
            print("n respuestas: ", n_respuestas)
            while True:
                    if(n_respuestas >= 3):
                        state = "held"
                        #Hacer la chamba
                        archivo = open("procesos.txt","r+")
                        texto_en_archivo=("Proceso con id: ",nodos_adyacentes[0]," entra a seccion critica a las: ",str(datetime.datetime.now().hour),"hrs",str(datetime.datetime.now().minute),"min",str(datetime.datetime.now().second),"s","\n")
                        texto_en_archivo=''.join(texto_en_archivo)
                        archivo.write(texto_en_archivo)
                        print(archivo.readlines())
                        archivo.close()
                        nodo_c_1 = th.Thread(target=salir_client_1)
                        nodo_c_1.start()
                        time.sleep(1)
                        nodo_c_2 = th.Thread(target=salir_client_2)
                        nodo_c_2.start()
                        time.sleep(1)
                        nodo_c_3 = th.Thread(target=salir_client_3)
                        nodo_c_3.start()
                        time.sleep(1)
                        n_respuestas = 0
                        break
                    time.sleep(1)
                    print("en espera...")

#función para solicitar sección crítica a cliente 1
def client_1():
    global state
    global n_respuestas
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[0])
    message = {
        "solicitud":"request",
        "id":nodos_adyacentes[0]
    }
    print("Enviando solicitud de %s %s" % ("client_1", nodos_adyacentes[0]))
    socket.send_json(message)
    message = socket.recv_json()
    if(message["id"]==nodos_adyacentes[0] and message["solicitud"]=="accepted"):
        n_respuestas = n_respuestas + 1
        print("aceptado")
    print("Respuesta recibida de %s %s" % (nodos_adyacentes[0], message))

#función para solicitar sección crítica a cliente 2
def client_2():
    global state
    global n_respuestas
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[1])
    message = {
        "solicitud":"request",
        "id":nodos_adyacentes[0]
    }
    print("Enviando solicitud de %s %s" % ("client_1", nodos_adyacentes[1]))
    socket.send_json(message)
    message = socket.recv_json()
    if(message["id"]==nodos_adyacentes[0] and message["solicitud"]=="accepted"):
        n_respuestas = n_respuestas + 1
        print("aceptado")
    print("Respuesta recibida de %s %s" % (nodos_adyacentes[1], message))

#función para solicitar sección crítica a cliente 3
def client_3():
    global state
    global n_respuestas
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[2])
    message = {
        "solicitud":"request",
        "id":nodos_adyacentes[0]
    }
    print("Enviando solicitud de %s %s" % ("client_1", nodos_adyacentes[2]))
    socket.send_json(message)
    message = socket.recv_json()
    if(message["id"]==nodos_adyacentes[0] and message["solicitud"]=="accepted"):
        n_respuestas = n_respuestas + 1
        print("aceptado")
    print("Respuesta recibida de %s %s" % (nodos_adyacentes[2], message))

#función para salir de la sección crítica con cliente 1
def salir_client_1():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[0])
    message = {
        "solicitud":"released",
        "id":nodos_adyacentes[0]
    }
    socket.send_json(message)
    socket.recv_json()

#función para salir de la sección crítica con cliente 2
def salir_client_2():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[1])
    message = {
        "solicitud":"released",
        "id":nodos_adyacentes[0]
    }
    socket.send_json(message)
    socket.recv_json()

#función para salir de la sección crítica con cliente 3
def salir_client_3():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:"+nodos_adyacentes[2])
    message = {
        "solicitud":"released",
        "id":nodos_adyacentes[0]
    }
    socket.send_json(message)
    socket.recv_json()

#se inicia el nodo de servidor y se pregunta si se quiere entrar a la sección crítica
print("Estableciendo conexion...")
nodo_s = th.Thread(target=server)
nodo_s.start()
preguntar_seccion_critica()