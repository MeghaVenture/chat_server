# SERVER-SIDE FOR CHAT
# IMPORTS
import string
import threading
import socket
import time
import random

# VARIABLES
START_PORT = 8000  # TASK requires 8000 and 8001
MAIN_PORT = 8001

SERVER_IP = '0.0.0.0'
    # socket.gethostbyname(socket.gethostname())  # finds machine-running-program's local IP
START_ADDRESS = (SERVER_IP, START_PORT)
MAIN_ADDRESS = (SERVER_IP, MAIN_PORT)

CODE_LENGTH = 50
FORMAT = "utf-8"
TIME_FORMAT = "%Y:%m:%d_%H:%M:%S"
MAX_MSG_SIZE = 1024  # HEADER instead?

DISCONNECT_CODE = "!<!<!DISCONNECT!>!>!"

idens_and_codes: []
codes = []
identifiers = []
connected_clients = []
clients_names = []
clients_lock = threading.Lock()

# SERVERS
# NOTE: AF_INET => IPv4 addresses = Local IP;
# NOTE: SOCKET_STREAM => TCP socket/method
s_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
s_server_socket.bind(START_ADDRESS)

m_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
m_server_socket.bind(MAIN_ADDRESS)


# FUNCTIONS
def log_server(msg):
    with open('server_log.txt', 'a') as log:
        log.write(f"{msg} \n")


def log_lists(list_to_log):
    list_name = str(list_to_log)
    message = f'{get_time()} | {list_name}: {list_to_log}'
    log_server(message)


def get_time():
    t = time.strftime(TIME_FORMAT)
    return t


def broadcast(message): # takes UN-encoded messages
    ''' Sends, logs, prints, & encodes the message,
    to all connected clients '''
    log_server(message)
    print(message)
    with clients_lock:
        for client in connected_clients:
            client.send(message.encode(FORMAT))


def make_unique_code(identifier):
    all_characters = string.ascii_letters + string.digits + string.punctuation
    try:
        code = "".join(random.sample(all_characters, CODE_LENGTH))
        if code not in codes:
            codes.append(code)
    finally:
        unique_code = code
        idens_and_codes.append((identifier, unique_code))
        log_lists(idens_and_codes)
    return unique_code


def remove_client(connection,server_address, client_address):
    with clients_lock:
        index = connected_clients.index(connection)
        client_name = clients_names[index]
        broadcast(f"[DISCONNECTION] {get_time()} | {client_name} at {client_address} has disconnected from {server_address}")
        connected_clients.remove(connection)
        clients_names.remove(client_name)
    connection.close()
    broadcast(f"[CONNECTION COUNT] {get_time()} | {threading.activeCount() - 1} current connections.")


def handle_client(connection, server_address, client_address, client_name):
    ''' Handles maintaining the client connection: 
    receiving and broadcasting messages, 
    and client's clean disconnection from server.'''

    broadcast(f"[NEW CONNECTION] {get_time()} | {client_address} connected as {client_name} to {server_address}.")
    try:
        while True:
            recv_message = connection.recv(MAX_MSG_SIZE).decode(FORMAT)
            msg_time = get_time()
            if not recv_message:  # (if none) = handles empty messages
                break
            if recv_message == DISCONNECT_CODE:
                break
            broadcast(f"[{client_address}] {msg_time} |  {client_name}: {recv_message}")
    finally:
        remove_client(connection, server_address, client_address)


def main(port):
    '''Sets server to listen for clients,
    creates a thread for each client '''

    # change based on which port is using function
    if port == START_PORT:
        chat_server = s_server_socket
        server_address = START_ADDRESS
    elif port == MAIN_PORT:
        chat_server = m_server_socket
        server_address = START_ADDRESS

    else:
        print(f"[PORT ERROR] {port} is not an accepted port.")

    broadcast(f"[SERVER STARTED] {get_time()} | {server_address} running.")
    chat_server.listen()
    broadcast(f"[LISTENING] {get_time()} | {server_address} is listening.")
    while True:
        (connection, client_address) = chat_server.accept()
        with clients_lock:  # Makes sure only one at a time
            connection.send('client_name?'.encode(FORMAT))
            client_name = connection.recv(MAX_MSG_SIZE).decode(FORMAT)
            clients_names.append(client_name)
            log_lists(clients_names)
            connected_clients.append(connection)
            log_lists(connected_clients)
            if server_address == START_ADDRESS:
                connection.send('Identifier?'.encode(FORMAT))
                identifier = connection.recv(MAX_MSG_SIZE).decode(FORMAT)
                identifiers.append(identifier)
                log_lists(identifiers)
                connection.send(make_unique_code(identifier))     # make_unique_code returns unique_code
            elif server_address == MAIN_ADDRESS:
                connection.send('id_code_pair?'.encode(FORMAT))
                id_code_pair = connection.recv(MAX_MSG_SIZE).decode(FORMAT)
                if id_code_pair not in idens_and_codes:
                    remove_client(connection, server_address, client_address)
                    break
            else:
                remove_client(connection, server_address, client_address)
                break
            thread = threading.Thread(target=handle_client, args=(connection, server_address, client_address, client_name))
            thread.start()
            connection.send(f"[CONNECTED] {get_time()} | you are connected to {server_address}.")
            broadcast(f'[CONNECTED] {get_time()} | {client_address} is now connected as {client_name} to {server_address}.')
            broadcast(f"[CONNECTION COUNT] {threading.activeCount() - 1} current connections to {server_address}.")


# want to use as not main?
if __name__ == "__main__":
#    s_server_thread = threading.Thread(target=main, args=START_PORT)
#    s_server_thread.start()
#    m_server_thread = threading.Thread(target=main, args=START_PORT)
#    m_server_thread.stat()
    main(START_PORT)
    main(MAIN_PORT)