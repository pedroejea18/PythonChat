Server.py:
This class implements a chat server that accepts UDP connections, manages users (including administrators), and allows two-way communication between clients. Additionally, it provides the ability for an administrator to kick out a specific user using a special command.
To ban a user, you have to run the client.py and name yourself as "admin", then once you type the token, you should be able to chat as a normal client would do, but because you name youself as an admin before now you can ban people typing "/ban userToken". If for example
you connected the client2 at the same time you could ban this client2, so in the console of this client2 should appear the message "You have been banned", and this client will get kicked from the chat.

To run it correctly you have to open first the server.py then open a client (You can open as many client as you wish, I just created 2 files of client just to try), once you put a name to the client and type the token you should be able to chat and see the chat history 
on the server, you can open the clients you want, the program should be capable of chat with each other.

I also created a funcionality that saves the client info in a txt file, in this file you will see the ip of the client, his name and his token. So when you want to ban a user you just go to that txt file copy the token and paste on the console, once its banned the user info should dissapear from the txt.
