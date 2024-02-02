import socket
import uuid

IP_Serv = '192.168.1.135' #insert your ipv4 address
port = 9000

usersTokenTxt = "users_token.txt"

def generate_token():
    return str(uuid.uuid4())

def save_user_tokens(clients):
    with open(usersTokenTxt, "w") as file:
        for adress, client_info in clients.items():
            file.write(f"{adress[0]}:{adress[1]}:{client_info['name']}:{client_info['token']}\n")

# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the specified IP and port
server.bind((IP_Serv, port))

clients = {}
admin = False

while True:
    try:
        # Receive data and address from the client
        message, adress = server.recvfrom(1024)
        if not message:
            continue
    except ConnectionResetError:
        print("Connection error. Ignoring the package.")
        continue

    # Check if the client is not in the list of connected clients
    if adress not in clients:
        # Decode the received message, assumed to be the client's name
        name = message.decode('utf-8')
        token = generate_token()

        # Check if the client is an admin
        if name.lower() == "admin":
            clients[adress] = {'name': name, 'token': token, 'admin': True}
        else:
            clients[adress] = {'name': name, 'token': token}

        print(f"New connection established: {name} - {adress[0]}:{adress[1]} - Token: {token}")
        
        # Send the generated token back to the client
        server.sendto(token.encode('utf-8'), adress)
        
        # Save the user tokens to a file
        save_user_tokens(clients)

    else:
        # Process messages from already connected clients
        message = message.decode('utf-8')
        parts = message.split(': ', 1)

        if len(parts) == 2:
            token, message = parts
            client = next((client for client in clients.values() if client['token'] == token), None)

            if client:
                print(f"{client['name']} - {message}")
                if client.get('admin', True):  
                    if message.startswith("/ban"):
                        # Process ban command from admin
                        parts_ban = message.split(' ')
                        if len(parts_ban) == 2:
                            token_ban = parts_ban[1]

                            if token_ban in [cliente_info['token'] for cliente_info in clients.values()]:
                                adress_ban = next(adress for adress, info in clients.items() if info['token'] == token_ban)
                                del clients[adress_ban]
                                print(f"Client with the token {token_ban} has been banned.")
                                save_user_tokens(clients)
                                server.sendto("BANNED".encode('utf-8'), adress_ban) 
                            else:
                                print(f"Client with token {token_ban} not found.")
                        else:
                            print("Incorrect ban command format.")
                    else:
                        # Broadcast the message to all connected clients
                        for client_adress, client_info in clients.items():
                            if client_adress != adress:
                                try:
                                    send_message = f"{client['name']} - {message}"
                                    server.sendto(send_message.encode('utf-8'), client_adress)
                                except ConnectionResetError:
                                    print(f"Connection error when sending message to {client_info['name']}.")
                else:
                    # Broadcast the message to all connected clients (non-admin)
                    for client_adress, client_info in clients.items():
                        if client_adress != adress:
                            try:
                                send_message = f"{client['name']} - {message}"
                                server.sendto(send_message.encode('utf-8'), client_adress)
                            except ConnectionResetError:
                                print(f"Connection error when sending message to {client_info['name']}.")
            else:
                print("Invalid token.")
        else:
            print("Invalid message format.")
