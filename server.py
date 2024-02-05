import socket
import uuid

Server_IP = '192.168.1.135'
Port = 9000

User_Tokens_File = "users_token.txt"
Admin_Password = "admin"  # Replace with the desired password for the admin

def generate_token():
    return str(uuid.uuid4())

def save_user_tokens(clients):
    with open(User_Tokens_File, "w") as file:
        for address, client_info in clients.items():
            file.write(f"{address[0]}:{address[1]}:{client_info['name']}:{client_info['token']}\n")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((Server_IP, Port))

clients = {}

while True:
    try:
        message, address = server_socket.recvfrom(1024)
        if not message:
            continue
    except ConnectionResetError:
        print("Connection error. Ignoring the packet.")
        continue

    if address not in clients:
        name = message.decode('utf-8')
        if name.lower() == "admin":
            # Request password from the admin
            server_socket.sendto("ADMIN_PASSWORD".encode('utf-8'), address)
            entered_password, _ = server_socket.recvfrom(1024)
            if entered_password.decode('utf-8') == Admin_Password:
                server_socket.sendto("PASSWORD CORRECT".encode('utf-8'), address)
                token = generate_token()
                clients[address] = {'name': name, 'token': token, 'admin': True}
                print(f"New admin connected: {name} - {address[0]}:{address[1]} - Token: {token}")
                server_socket.sendto(token.encode('utf-8'), address)
                save_user_tokens(clients)
            else:
                print("Incorrect password for the admin.")
                server_socket.sendto("INCORRECT PASSWORD".encode('utf-8'), address)
                continue
        else:
            token = generate_token()
            clients[address] = {'name': name, 'token': token}
            print(f"New connection established: {name} - {address[0]}:{address[1]} - Token: {token}")
            server_socket.sendto(token.encode('utf-8'), address)
            save_user_tokens(clients)
    else:
        message = message.decode('utf-8')
        parts = message.split(': ', 1)

        if len(parts) == 2:
            token, message = parts
            client = next((client for client in clients.values() if client['token'] == token), None)

            if client:
                print(f"{client['name']} - {message}")

                # If the client entered the name "admin", it will become an administrator
                if client.get('admin', False):  # Check if the client is an administrator
                    if message.startswith("/ban"):
                        parts_ban = message.split(' ')
                        if len(parts_ban) == 2:
                            token_ban = parts_ban[1]

                            if token_ban in [client_info['token'] for client_info in clients.values()]:
                                address_ban = next(addr for addr, info in clients.items() if info['token'] == token_ban)
                                del clients[address_ban]
                                print(f"Client with token {token_ban} has been banned.")
                                save_user_tokens(clients)
                                server_socket.sendto("BANNED".encode('utf-8'), address_ban)  # Send ban message
                            else:
                                print(f"Client with token {token_ban} not found.")
                        else:
                            print("Incorrect ban command format.")
                    # If the "admin" doesn't write something starting with /ban, it will be considered as a normal message:
                    else:
                        for client_address, client_info in clients.items():
                            if client_address != address:
                                try:
                                    message_to_send = f"{client['name']} - {message}"
                                    server_socket.sendto(message_to_send.encode('utf-8'), client_address)
                                except ConnectionResetError:
                                    print(f"Connection error while sending message to {client_info['name']}.")
                # If the client is not "admin":
                # This sends a normal message
                else:
                    for client_address, client_info in clients.items():
                        if client_address != address:
                            try:
                                message_to_send = f"{client['name']} - {message}"
                                server_socket.sendto(message_to_send.encode('utf-8'), client_address)
                            except ConnectionResetError:
                                print(f"Connection error while sending message to {client_info['name']}.")

            else:
                print("Invalid token.")
        else:
            print("Invalid message format.")
