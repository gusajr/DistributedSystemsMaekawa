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
    recibido = s.recv(1024).decode("utf-8")
    print(recibido)
    if(recibido == "inicio"):
        time.sleep(5)
        print("enviando respuesta")
        s.sendto(txt.encode("utf-8"),('127.0.0.1', port))

#s.recv(1024).decode("utf-8")
# receive data from the server 
#print (s.recv(1024).decode("utf-8") )
# close the connection 
#s.close()