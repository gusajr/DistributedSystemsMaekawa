import time
import zmq
import threading as th
import datetime

procesosTotales = ["5555","5556","5557","5558"]

#Clase nodo que tendrá sus atributos para trabajar de forma independiente
class Nodo:
    def __init__(self,id):
        self.id = id
        #dependiendo del tipo de id se define su matriz adyacente
        if(id=="5555"):
            matrizAdyacente = ["5555","5556","5557"]
        if(id=="5556"):
            matrizAdyacente = ["5556","5555","5558"]
        if(id=="5557"):
            matrizAdyacente = ["5557","5555","5558"]
        if(id=="5558"):
            matrizAdyacente = ["5558","5556","5557"]
        #se asigna la matriz adyacente a ese proceso
        self.matrizAdyacente = matrizAdyacente
        #estado inicial del proceso
        self.estado = "released"
        self.votacion = False
        self.pendientes = []
        self.n_respuestas = 0
        #hilo para comunicación con los demás nodos
        self.cl_1 = th.Thread(target=self.iniciarCliente, args=(self.matrizAdyacente[0],0,))
        self.cl_2 = th.Thread(target=self.iniciarCliente, args=(self.matrizAdyacente[1],1,))
        self.cl_3 = th.Thread(target=self.iniciarCliente, args=(self.matrizAdyacente[2],2,))
        #hilo para recibir notificaciones de otros nodos
        self.serv_1 = th.Thread(target=self.iniciarServidor, args=(self.id,))
        self.sockets_cl = []
        self.contexts = []
        self.cl_1.start()
        self.cl_2.start()
        self.cl_3.start()
        self.serv_1.start()
        self.seccion_critica = False
        self.preguntar_seccion_critica = th.Thread(target=self.preguntar_seccion_critica_1)
        self.preguntar_seccion_critica.start()

    #función para preguntar de forma indefinida si se desea entrar a la sección crítica
    def preguntar_seccion_critica_1(self):
        while True:
            if(input("¿Desea entrar a la sección crítica?")):
                self.estado="wanted"
                print(self.estado)
                message = {
                    "solicitud":"request",
                    "id":self.id
                }
                self.sockets_cl[0].send_json(message)
                self.sockets_cl[1].send_json(message)
                self.sockets_cl[2].send_json(message)

    #función para iniciar el puerto servidor
    def iniciarServidor(self, puerto):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://*:"+puerto)
        print(puerto)
        print("se ha iniciado el puerto servidor")
        while True:
            print("esperando mensaje...")
            message = socket.recv_json()
            print("mensaje recibido: ", message)
            message = self.valorarRespuesta(message)
            #seed(1)
            #time.sleep(random())
            #socket.send_json(message)
            if(message is not None):
                self.sockets_cl[0].send_json(message)
                self.sockets_cl[1].send_json(message)
                self.sockets_cl[2].send_json(message)

    #función para iniciar comunicación con distintos nodos
    def iniciarCliente(self, puerto, n_socket):
        self.contexts.append(zmq.Context())
        self.sockets_cl.append(self.contexts[n_socket].socket(zmq.PUSH))
        self.sockets_cl[n_socket].connect("tcp://localhost:"+puerto)

    #función para saber cuál fue la respuesta de parte de los nodos
    def valorarRespuesta(self,message):
        if(message["solicitud"]=="request"):
            if(self.estado=="held" or self.votacion==True):
                if(message["id"] not in self.pendientes):
                    self.pendientes.append(message["id"])
                    print("procesos pendientes:", self.pendientes)
                    print("se encola proceso con id:", message["id"])
                    return    {
                        "solicitud":"failed",
                        "id":message["id"]
                    }
            else:
                self.votacion = True
                print("entra en request")
                return {
                    "solicitud":"accepted",
                    "id":message["id"]
                }
                
        if(message["solicitud"]=="released"):
            print("entra con released")
            if self.pendientes:
                print("entra en pendiente")
                self.votacion = True
                return{
                    "solicitud":"accepted",
                    "id":self.pendientes.pop(0)
                    }
            else:
                self.votacion = False
                return{
                    "solicitud":"finished",
                    "id":message["id"]
                }

        if(message["solicitud"]=="accepted" and message["id"]==self.id):
            self.n_respuestas = self.n_respuestas + 1
            print("n_respuestas: ", self.n_respuestas)
            if(self.n_respuestas==3):
                self.n_respuestas=0
                self.entrar_seccion_critica()
    
    #función para la sección crítica
    def entrar_seccion_critica(self):
        archivo = open("procesos.txt","r+")
        texto_en_archivo=("Proceso con id: ",self.id," entra a seccion critica a las: ",str(datetime.datetime.now().hour),"hrs",str(datetime.datetime.now().minute),"min",str(datetime.datetime.now().second),"s","\n")
        texto_en_archivo=''.join(texto_en_archivo)
        archivo.write(texto_en_archivo)
        print(archivo.readlines())
        archivo.close()
        time.sleep(10)
        message = {
            "solicitud":"released",
            "id":self.id
        }
        self.sockets_cl[0].send_json(message)
        self.sockets_cl[1].send_json(message)
        self.sockets_cl[2].send_json(message)

if __name__ == "__main__":
    #pregunta por el puerto de preferencia
    id = input("Numero de puerto, inserte ya sea 5555, 5556, 5557 o 5558 (no deben repetirse en las distintas instancias del programa): ")
    if(id not in procesosTotales):
        while(True):
            id=input("Número de proceso no válido, inserte ya sea 5555, 5556, 5557 o 5558 (no deben repetirse en las distintas instancias del programa): ")
            if(id in procesosTotales):
                break

    #se crea objeto nodo
    nodo1 = Nodo(id)