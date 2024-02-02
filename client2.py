import socket
import os
import threading

conexion_adress = '192.168.1.135' #insert your ipv4 address
conexionPort = 9000

client_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def getToken():
    name = input("Your name: ")
    client_Socket.sendto(name.encode('utf-8'), (conexion_adress, conexionPort))    
    answer, _ = client_Socket.recvfrom(1024)
    token = answer.decode('utf-8')
    print(f"Your token is: {token}")
    return token

def receive_messages():
    while True:
        try:
            message, _ = client_Socket.recvfrom(1024)
            if message:
                decoded_Message = message.decode('utf-8')
                if decoded_Message == "BANNED":
                    print("You have been banned. Leaving chat...")
                    os._exit(0)  
                else:
                    print(decoded_Message)
        except ConnectionResetError:
            print("Connection error when receiving messages from other clients.")

token = getToken()
correctToken = False

# Start a thread to continuously receive messages
reception_thread = threading.Thread(target=receive_messages, daemon=True)
reception_thread.start()

while True:
    while not correctToken:
        # Wait for the user to enter the correct token
        userToken = input("Enter the token to write: ")
        if userToken == token:
            correctToken = True
            print("The token is correct, you can chat now.")

    # Get user input and send it to the server
    message = input()
    
    message_with_token = f"{token}: {message}"
    client_Socket.sendto(message_with_token.encode('utf-8'), (conexion_adress, conexionPort))
