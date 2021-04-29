# Import socket module 
import socket  
import time           
  
# Create a socket object 
s = socket.socket()         
  
# Define the port on which you want to connect 
port = 12345                
  
#while True:
# connect to the server on local computer 
s.connect(('127.0.0.1', port)) 

txt = ''

id = s.recv(1024).decode("utf-8")
print("id",id)

while True:
    respuesta = (bool(int(input("¿Desea entrar a la zona crítica? -> 0.No -> 1.Si: "))))
    if(respuesta):
        print(id)
        txt = txt, str(id)
        txt = ''.join(txt)
        s.sendto(txt.encode("utf-8"),('127.0.0.1', port))
        respuesta=False
    recibido = s.recv(1024).decode("utf-8")
    print(recibido)
    if(recibido == "inicio"):
        archivo = open("procesos.txt","r+")
        texto_en_archivo=("Proceso con id: ",str(id)," entró a zona crítica\n")
        texto_en_archivo=''.join(texto_en_archivo)
        archivo.write(texto_en_archivo)
        print(archivo.readlines())
        archivo.close()
        time.sleep(5)
        print("enviando respuesta")
        s.sendto(txt.encode("utf-8"),('127.0.0.1', port))

#s.recv(1024).decode("utf-8")
# receive data from the server 
#print (s.recv(1024).decode("utf-8") )
# close the connection 
#s.close()