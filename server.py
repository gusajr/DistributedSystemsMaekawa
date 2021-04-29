# first of all import the socket library 
import socket      
import math
import numpy as np 

import logging
import time
import _thread as th
import numpy as np
import math
import queue as q

#Variables globales que utilizan todos los hilos
global num_procesos
global procesos
global raiz_np
global num_procesos_conectados_raiz
global c
global s

archivo = open("procesos.txt","w")
archivo.close()

class Proceso():
    def __init__(self, id):
        #atributos que maneja cada proceso | estado inicial
        self.p_adyacentes = []
        self.p_id = id
        self.p_estado = 'released'
        self.p_votacion = False
        self.p_peticiones = q.Queue()
        self.p_mensaje = 'released'
        self.p_respuestas_recibidas = 0

    def entrar_seccion_critica(self, clientsocket):
        #if(self.getName() != threading.current_thread().getName()):
        self.p_estado='wanted'
        print("pidiendo entrar a seccion critica")
        self.informar_demas_procesos('request')
        print("respuestas recibidas", self.p_respuestas_recibidas)
        while True:
            if(self.p_respuestas_recibidas == num_procesos_conectados_raiz+1): #Es mas uno porque se incluyó al proceso mismo
                #txt = "inicio"
                #c.sendto(txt.encode("utf-8"),('127.0.0.1',self.p_id))
                print("entra en igual")
                while True:
                    print("esperando respuesta")
                    recibido = clientsocket.recv(1024).decode("utf-8") #Se queda esperando, solo sirve para ultimo socket
                    print("recibido",recibido)
                    if(int(recibido) == self.p_id):
                        #print("recibido")
                        break
                self.p_estado = 'held'
                print("reiniciando respuestas...")
                self.p_respuestas_recibidas = 0
                self.salir_seccion_critica()
                break
    
    def salir_seccion_critica(self):
        print("saliendo de sección crítica ...")
        self.p_estado = 'released'
        for i in range(num_procesos_conectados_raiz+1):    
            procesos[i].informar_demas_procesos('release')
        print("proceso:", self.p_id, "ha salido de la sección crítica")

    def informar_demas_procesos(self, mensaje):
        print("informando a los demás procesos")
        for i in range(num_procesos_conectados_raiz+1):
            #print("valor de i: ", i, num_procesos_conectados_raiz)
            print("informando a proceso",i)
            procesos[i].p_mensaje = mensaje
            procesos[i].recepcion_de_mensaje(mensaje, self.p_id)

    def recepcion_de_mensaje(self, mensaje, id):
        print("se recibió mensaje", mensaje, "de", id, "para", self.p_id)
        if(mensaje == 'request'):
            if(self.p_estado == 'held' or self.p_votacion == True):
                print("entra en or")
                for i in range(num_procesos):
                    if(procesos[i].p_id==self.p_id):
                        procesos[i].p_peticiones.put(id)
                #procesos[self.p_id].p_peticiones.put(id)
            else:
                print("entra en else")
                print(num_procesos)
                for i in range(num_procesos):
                    if(procesos[i].p_id==id):
                        procesos[i].p_respuestas_recibidas = procesos[i].p_respuestas_recibidas + 1
                #procesos[id].p_respuestas_recibidas = procesos[id].p_respuestas_recibidas + 1
                self.p_votacion = True

        if(mensaje == 'release'):
            if(not self.p_peticiones.empty()):
                for i in range(num_procesos):
                    if(procesos[i].p_id==id):
                        id=procesos[i].p_peticiones.get()
                #id = procesos[id].p_peticiones.get()
                print("proceso sacado de la cola: ", id)
                for i in range(num_procesos):
                    if(procesos[i].p_id==id):
                        procesos[i].p_respuestas_recibidas = procesos[i].p_respuestas_recibidas + 1
                #procesos[id].p_respuestas_recibidas = procesos[id].p_respuestas_recibidas + 1
                self.p_votacion = True
            else:
                self.p_votacion = False

#función de trabajo que hace el proceso en sección crítica
def worker():
        logging.debug('Entrando a sección crítica')
        #time.sleep(0.2)
        #for i in range(numero_procesos):
        #    if(procesos[i].getName() == threading.current_thread().getName()):
        #        procesos[i].salir_seccion_critica()
        logging.debug('Terminando operación')

        #for i in range(numero_procesos):
        #    print("estado actual de proceso", procesos[i].getName())
        #    print(procesos[i].p_id,procesos[i].p_estado,procesos[i].p_votacion,procesos[i].p_peticiones, 
        #        procesos[i].p_respuestas_recibidas)

def on_new_client(clientsocket,addr):
    firstime = True
    while True: #------------>Una vez que ya se manda el id hay que ver como poder hacer que ese paso ya no lo haga
        #clientsocket.send(recibido)
        
        if(firstime):
            txt = "inicio"
            c.sendto(txt.encode("utf-8"),('127.0.0.1',addr[1]))
            firstime = False
        
        recibido = clientsocket.recv(1024).decode("utf-8")
        print("recibida la respuesta...")
        for i in range(num_procesos):
            if(int(recibido)==procesos[i].p_id):
                procesos[i].entrar_seccion_critica(clientsocket)
        #do some checks and if msg == someWeirdSignal: break:
        #print (addr, ' >> ', recibido)
        #proceso.entrar_seccion_critica()
        #msg = raw_input('SERVER >> ')
        #Maybe some code to compute the last digit of PI, play game or anything else can go here and when you are done.
        
    clientsocket.close()

# next create a socket object 
s = socket.socket()         
print ("Socket successfully created")
  
# reserve a port on your computer in our 
# case it is 12345 but it can be anything 
port = 12345                
  
# Next bind to the port 
# we have not typed any ip in the ip field 
# instead we have inputted an empty string 
# this makes the server listen to requests 
# coming from other computers on the network 
s.bind(('', port))         
print ("socket binded to %s" %(port)) 
  
# put the socket into listening mode 
s.listen(5)     
print ("socket is listening")            
  
txt = 'Thank you for connecting'

c_b = 0
addr_b = 0
cont = 0


procesos = []
procesos_matriz = []

# a forever loop until we interrupt it or 
# an error occurs 
while True: 
    # Establish connection with client. 
    c, addr = s.accept()
    #th.start_new_thread(entrar_seccion_critica())
    #if(c,addr != c_b,addr_b):
    print ('Got connection from', c, addr[1] )
    procesos.append(Proceso(addr[1]))
    c.sendto(str(procesos[cont].p_id).encode("utf-8"),addr)
    th.start_new_thread(on_new_client,(c,addr))
    #th.start_new_thread(procesos[cont].entrar_seccion_critica())
    print(procesos[0].p_id)
    print("conexion y dirección:",cont, procesos)
    print(len(procesos))
    num_procesos = len(procesos)
    num_procesos_conectados_raiz = int(math.sqrt(len(procesos)))
    cont = cont + 1
    #print("num pro:", num_procesos_conectados/(math.sqrt(len(procesos))))
    if(num_procesos_conectados_raiz/(math.sqrt(len(procesos))) != 1): #or num_procesos_conectados_raiz!=1):
        print("numero de procesos incorrecto:", num_procesos_conectados_raiz)
    else:
        #np.reshape(raiz_np,raiz_np)
        respuesta = bool(int(input("¿Quiere comenzar el trabajo en equipo? -> 0.No -> 1.Si: ")))
        if(respuesta):
            for i in range(cont):
                procesos_matriz.append(procesos[i].p_id)

            procesos_matriz = np.asarray(procesos_matriz).reshape(num_procesos_conectados_raiz,num_procesos_conectados_raiz)
            print(procesos_matriz)
            #se agregan los procesos del subconjunto
            i=0
            for j in range(num_procesos_conectados_raiz):
                for k in range(num_procesos_conectados_raiz):
                    procesos[i].p_adyacentes = np.concatenate((procesos_matriz[j,:],procesos_matriz[:,k]),axis=0)
                    procesos[i].p_adyacentes = procesos[i].p_adyacentes[procesos[i].p_adyacentes != procesos[i].p_id]
                    procesos[i].p_adyacentes = np.append(procesos[i].p_adyacentes, procesos[i].p_id)
                    #procesos[i].p_id = i
                    i = i + 1
            
            #while True:
            #recibido = c.recv(1024).decode("utf-8")
            #for i in range(num_procesos_conectados_raiz):
                #if(int(recibido)==procesos[i].p_id):
                    #procesos[i].entrar_seccion_critica()
            #print(recibido)