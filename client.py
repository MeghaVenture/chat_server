# CLIENT-SIDE FOR CHAT
# IMPORTS
import threading
import socket
import uuid

# VARIABLES    #? import variable file to improve ?
START_PORT = 8000
MAIN_PORT = 8001

SERVER_IP = '127.0.0.1'  # local or web? task does not state
CLIENT_ADDRESS = socket.gethostbyname(socket.gethostname())   # finds machine-running-program's local IP

START_ADDRESS = (SERVER_IP, START_PORT)
MAIN_ADDRESS = (SERVER_IP, MAIN_PORT)

FORMAT = "utf-8"
MAX_MSG_SIZE = 1024     # HEADER instead?
DISCONNECT_CODE = "!<!<!DISCONNECT!>!>!"

identifier = uuid.uuid4()
client_name = input("Enter your name: ")

# CONNECT TO SERVER
# AF_INET => IPv4 addresses = Local IP;
# SOCKET_STREAM => TCP socket/method
client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
client_socket.connect(START_ADDRESS)


# FUNCTIONS
def receive():
    while True:
        try:
            message = client.recv(MAX_MSG_SIZE).decode(FORMAT)
            if message == "client_name?":
                client.send(client_name.encode(FORMAT))
            elif message == "Identifier?":
                client.send(identifier.encode(FORMAT))
                unique_code = client.recv(MAX_MSG_SIZE).decode(FORMAT)
                switch_port(identifier, unique_code, message)
            elif message == 'id_code_pair?':
                id_code_pair = (identifier, unique_code)
                client.send(id_code_pair.encode(FORMAT))
            else:
                print(message)
        except:
            print(f"[FATAL ERROR] you have been disconnected from the SERVER.")
            client.send(DISCONNECT_CODE)
            client.close()
            break


def switch_port(new_address):
    client.send(DISCONNECT_CODE)
    client.connect(new_address)


def send():
    message = input("")
    client.send(message.encode(FORMAT))


# RECEIVE THREAD
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# SEND THREAD
send_thread = threading.Thread(target=send)
send_thread.start()

