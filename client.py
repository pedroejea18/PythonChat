import socket
import os
import threading

Server_Address = '192.168.1.135'
Server_Port = 9000

Client_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_token():
    name = input("Enter your name: ")
    Client_Socket.sendto(name.encode('utf-8'), (Server_Address, Server_Port))
    
    response, _ = Client_Socket.recvfrom(1024)
    if response.decode('utf-8') == "ADMIN_PASSWORD":
        # If the name is "admin", request the admin's password
        admin_password = input("Enter the admin password: ")
        Client_Socket.sendto(admin_password.encode('utf-8'), (Server_Address, Server_Port))
        admin_response, _ = Client_Socket.recvfrom(1024)
        if admin_response.decode('utf-8') == "PASSWORD CORRECT":
            print("Admin password correct. You are now an administrator.")
            # Receive the admin's token after successful authentication
            admin_token, _ = Client_Socket.recvfrom(1024)
            return admin_token.decode('utf-8')
        else:
            print("Incorrect admin password.")
            os._exit(0)  # Exit the program if the admin password is incorrect
    else:
        token = response.decode('utf-8')
        print(f"Your token is: {token}")
        return token

def receive_messages():
    while True:
        try:
            message, _ = Client_Socket.recvfrom(1024)
            if message:
                decoded_message = message.decode('utf-8')
                if decoded_message == "BANNED":
                    print("You have been banned. Exiting the chat.")
                    os._exit(0)  # Exit the program
                else:
                    print(decoded_message)
        except ConnectionResetError:
            print("Connection error while receiving messages from other clients.")

token = get_token()
correct_token = False

# Start a thread to receive messages while the client waits for user input
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

while True:
    while not correct_token:
        if token == "CONNECTION_ADM":
            correct_token = True
        else:
            user_token = input("Enter the token to write: ")
            if user_token == token:
                correct_token = True
                print("Token is correct, you can now chat.")
                
    message = input("Write: \n")
    
    message_with_token = f"{token}: {message}"
    Client_Socket.sendto(message_with_token.encode('utf-8'), (Server_Address, Server_Port))
