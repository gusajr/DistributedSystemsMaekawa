import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
message = {
        "solicitud":"request",
        "id":"5556"
    }
socket.send_json(message)
message=socket.recv()
print(message)
print("mensaje enviado")