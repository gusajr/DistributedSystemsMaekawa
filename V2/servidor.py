#importación de bibliotecas utilizadas
import socket      
import math
import logging
import _thread as th
import numpy as np
import queue as q

#variables globales que utilizan todos los hilos
global num_procesos
global procesos
global raiz_np
global num_procesos_conectados_raiz
global c
global s

#archivo que modificarán los procesos
archivo = open("procesos.txt","w")
archivo.close()

class Proceso():
    def __init__(self, id):
        #atributos que maneja cada proceso | estado inicial
        self.p_adyacentes = []
        self.p_id = id
        self.p_estado = "released"
        self.p_votacion = False
        self.p_peticiones = q.Queue()
        self.p_mensaje = "released"
        self.p_respuestas_recibidas = 0
        self.p_lock = th.allocate_lock()

    def entrar_seccion_critica(self, clientsocket):
        self.p_estado='wanted'
        print("pidiendo entrar a seccion critica")
        self.informar_demas_procesos("request")
        print("respuestas recibidas", self.p_respuestas_recibidas)
        #self.p_lock.acquire()
        #with on_new_client_lock:
        while True:
            if(self.p_respuestas_recibidas == num_procesos_conectados_raiz+1): #Es mas uno porque se incluyó al proceso mismo
                print("entra en igual")
                while True:
                    txt = "inicio"
                    clientsocket.sendto(txt.encode("utf-8"),("127.0.0.1",addr[1]))
                    print("esperando respuesta")
                    recibido = clientsocket.recv(1024).decode("utf-8") #Se queda esperando, solo sirve para ultimo socket
                    print("recibido",recibido)
                    if(int(recibido) == self.p_id):
                        break
                self.p_estado = "held"
                print("reiniciando respuestas...")
                self.p_respuestas_recibidas = 0
                self.salir_seccion_critica()
                #self.p_lock.release()
                break
    
    def salir_seccion_critica(self):
        print("saliendo de sección crítica ...")
        self.p_estado = "released"
        for i in range(num_procesos_conectados_raiz+1):    
            procesos[i].informar_demas_procesos("release")
        print("proceso:", self.p_id, "ha salido de la sección crítica")

    def informar_demas_procesos(self, mensaje):
        print("informando a los demás procesos")
        for i in range(num_procesos_conectados_raiz+1):
            print("informando a proceso",i)
            procesos[i].p_mensaje = mensaje
            procesos[i].recepcion_de_mensaje(mensaje, self.p_id)

    def recepcion_de_mensaje(self, mensaje, id):
        print("se recibió mensaje", mensaje, "de", id, "para", self.p_id)
        if(mensaje == "request"):
            if(self.p_estado == "held" or self.p_votacion == True):
                print("entra en or")
                for i in range(num_procesos):
                    if(procesos[i].p_id==self.p_id):
                        procesos[i].p_peticiones.put(id)
                        
            else:
                print("entra en else")
                print(num_procesos)
                for i in range(num_procesos):
                    if(procesos[i].p_id==id):
                        procesos[i].p_respuestas_recibidas = procesos[i].p_respuestas_recibidas + 1
                self.p_votacion = True

        if(mensaje == "release"):
            if(not self.p_peticiones.empty()):
                for i in range(num_procesos):
                    if(procesos[i].p_id==id):
                        id=procesos[i].p_peticiones.get()

                        #for j in range(num_procesos):
                        #    if(procesos[j].p_id=id)
                print("proceso sacado de la cola: ", id)
                for i in range(num_procesos):
                    if(procesos[i].p_id==id):
                        procesos[i].p_respuestas_recibidas = procesos[i].p_respuestas_recibidas + 1
                
                #self.p_lock.release()
                #for i in range(num_procesos):
                #    if(procesos[i].p_id==id):
                #        procesos[i].entrar_seccion_critica()

                self.p_votacion = True
            else:
                self.p_votacion = False

on_new_client_lock = th.allocate_lock()
def on_new_client(clientsocket,addr):
    #firstime = True
    while True: 
        #if(firstime):
        recibido = clientsocket.recv(1024).decode("utf-8")
        #txt = "inicio"
        #clientsocket.sendto(txt.encode("utf-8"),("127.0.0.1",addr[1]))
        #firstime = False
        
        #Solo falta ver como sacar procesos de la cola
       
        with on_new_client_lock:
            print("recibida la respuesta...")
            for i in range(num_procesos):
                print("iteraciones:",i,"recibido:",recibido)
                if(int(recibido)==procesos[i].p_id):
                    procesos[i].entrar_seccion_critica(clientsocket)
                    #recibido=0
    clientsocket.close()

#se crea el socket 
s = socket.socket()         
print ("socket creado correctamente")
port = 12345                 
s.bind(('', port))         
print ("socket enlazado con %s" %(port)) 
  
#se pone el socket en modo de escucha
s.listen(5)     
print ("socket ") 
txt = "conectado..."

cont = 0
procesos = []
procesos_matriz = []

#loop para recibir peticiones y responderlas 
while True: 
    #se aceptan las solicitudes
    c, addr = s.accept()
    print ("Se obtuvo conexión de: ", c, addr[1] )
    procesos.append(Proceso(addr[1]))
    c.sendto(str(procesos[cont].p_id).encode("utf-8"),addr)
    th.start_new_thread(on_new_client,(c,addr))
    print(procesos[0].p_id)
    print("conexion y dirección:",cont, procesos)
    print(len(procesos))
    num_procesos = len(procesos)
    num_procesos_conectados_raiz = int(math.sqrt(len(procesos)))
    cont = cont + 1
    if(num_procesos_conectados_raiz/(math.sqrt(len(procesos))) != 1):
        print("numero de procesos incorrecto:", num_procesos_conectados_raiz)
    else:
        respuesta = bool(int(input("¿Quiere comenzar el trabajo en equipo? -> 0.No -> 1.Si: ")))
        if(respuesta):
            for i in range(cont):
                procesos_matriz.append(procesos[i].p_id)
            procesos_matriz = np.asarray(procesos_matriz).reshape(num_procesos_conectados_raiz,num_procesos_conectados_raiz)
            print(procesos_matriz)
            i=0
            for j in range(num_procesos_conectados_raiz):
                for k in range(num_procesos_conectados_raiz):
                    procesos[i].p_adyacentes = np.concatenate((procesos_matriz[j,:],procesos_matriz[:,k]),axis=0)
                    procesos[i].p_adyacentes = procesos[i].p_adyacentes[procesos[i].p_adyacentes != procesos[i].p_id]
                    procesos[i].p_adyacentes = np.append(procesos[i].p_adyacentes, procesos[i].p_id)
                    i = i + 1
            if(num_procesos_conectados_raiz == 1):
                num_procesos_conectados_raiz = num_procesos_conectados_raiz-1