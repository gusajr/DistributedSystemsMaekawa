
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

state = "released"
voted = False
pendient_queue = q.Queue()
n_respuestas = 0

def recibirRespuesta(socket):
    #print("entra aquí")
    message = socket.recv_json()#.decode("utf-8")
    print("Respuesta recibida:",message)
    return message

def enviarRespuesta(socket,message):
    socket.send_json(message)#message.encode('utf-8'))
    
def valorarRespuesta(socket,message):
    global voted
    global n_respuestas
    #print("valorando respuesta")
    #print(message, message["solicitud"], message["id"])
    if(message["solicitud"]=="request"):
        if(state=="held" or voted==True):
            pendient_queue.put(message["id"])
            #if(state=="released"):
                #encolar situacion
            print("se encola")
            return    {
                "solicitud":"failed",
                "id":nodos_adyacentes[0]
            }
        else:
            #se envia respuesta de aceptación
            voted = True
            return{
                "solicitud":"accepted",
                "id":nodos_adyacentes[0]
            }
            
    if(message["solicitud"]=="released"):
        print("entra con released")
        if(not pendient_queue.empty()):
            socket.connect("tcp://localhost:"+pendient_queue.get())
            socket.send(
                {
                "solicitud":"accepted",
                "id":nodos_adyacentes[0]
                }
            )
            voted = True
            #return 
        else:
            voted = False
    
    if(message["solicitud"]=="accepted"):
        n_respuestas = n_respuestas + 1
        #print("released")
        #if(cola no vacia) eliminar elemento y enviarle respuesta VOTED=true
        #else voted = false
    #if(message["solicitud"]=="wake up"):



def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:"+nodos_adyacentes[0])
    while True:
        #enviarRespuesta(socket,
        enviarRespuesta(socket,valorarRespuesta(socket,recibirRespuesta(socket)))
        time.sleep(1)
        #if(str(input("¿Salir? Responda salir"))):
        #    break

def client():
    global state
    global voted
    global n_respuestas
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    while True:
        if(bool(int(input("¿desea entrar a la zona crítica? 0.No, 1.Si: ")))):
            while(n_respuestas < 1):   
                state = "wanted"
                message = {
                    "solicitud":"request",
                    "id":nodos_adyacentes[0]
                    }
                #client_1(socket,json.dumps(message),nodos_adyacentes[0])
                #client_1(socket,json.dumps(message),nodos_adyacentes[1])
                #si pasa el test entonces se pone en held
                #zona critica
                #release
                #if(
                client_1(socket,message,nodos_adyacentes[0])#["solicitud"]=="accepted"):
                state = "held"
                print("aceptado")
                message = {
                    "solicitud":"released",
                    "id":nodos_adyacentes[0]
                }
                break

            n_respuestas = 0
            

            #elif(client_1(socket,message,nodos_adyacentes[0]=="failed")):
            #    while True:
            #        if(recibirRespuesta(socket)["solicitud"]=="accepted"):
            #            state = "held"
            #            print("aceptado")
            #            message = {
            #            "solicitud":"released",
            #            "id":nodos_adyacentes[0]
            #            }
            #            break

            print("llega hasta aqui")
            client_1(socket,message,nodos_adyacentes[0])
            state = "released"
            print("se aviso a los demás:",state,voted)
            #break
            

def client_1(socket, message, nodo_adyacente):
    socket.connect("tcp://localhost:"+nodo_adyacente)
    enviarRespuesta(socket,message)
    #print(message)
    message = recibirRespuesta(socket)
    #print("respuesta es: ",message)
    #return message
    #valorarRespuesta()

nodo_s = th.Thread(target=server)
nodo_c = th.Thread(target=client)

nodo_s.start()
nodo_c.start()