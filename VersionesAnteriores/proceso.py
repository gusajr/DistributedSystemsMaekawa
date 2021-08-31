#importar bibliotecas necesarias
import socket  
import time           
  
#crear socket
s = socket.socket()         
port = 12345                
s.connect(("127.0.0.1", port)) 
txt = ""
id = s.recv(1024).decode("utf-8")
print("id",id)

#Ciclo del proceso para entrar a sección crítica
while True:
    respuesta = (bool(int(input("¿Desea entrar a la sección crítica? -> 0.No -> 1.Si: "))))
    if(respuesta):
        print(id)
        txt = txt, str(id)
        txt = ''.join(txt)
        s.sendto(txt.encode("utf-8"),('127.0.0.1', port))
        #print("Se ha enviado el mensaje")
        respuesta=False
    recibido = s.recv(1024).decode("utf-8")
    print(recibido)
    if(recibido == "inicio"):
        archivo = open("procesos.txt","r+")
        texto_en_archivo=("Proceso con id: ",str(id)," entró a sección crítica\n")
        texto_en_archivo=''.join(texto_en_archivo)
        archivo.write(texto_en_archivo)
        print(archivo.readlines())
        archivo.close()
        time.sleep(5)
        print("enviando respuesta")
        s.sendto(txt.encode("utf-8"),('127.0.0.1', port))
        txt = ""
        recibido=""

#s.recv(1024).decode("utf-8")
#se reciben los datos desde el servidor
#print (s.recv(1024).decode("utf-8") )
#se cierra la coneccion
#s.close()