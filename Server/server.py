from queue import Queue
import socket
import threading
from time import sleep
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)               #Creates the socket for the server

print("Welcome to S354418's server. Follow the instructions below")
print("To write a message to the users, just type in the command line")
print("To get help just type --help")
print("Please follow the instructions to start the server, enjoy!")
print("Do you wanna define the IP and Port yourself? Y/N")

host_q = Queue()                                                                #Queue for host info
port_q = Queue()                                                                #Queue for port info
conn_q = Queue()                                                                #Queue for connection    
name_q = Queue()                                                                #Queue for nickname  

name_list = []                                                                  #List of all the nicknames for the clients
client_list = []                                                                #List of all the clients connected
msg_list = []                                                                   #List for the clients we want to message

wait_for_connection = threading.Event()                                         #Creates a "Event" so i can pause a bit of code until i give a green light to run.

#The check function. Checks if the user wants to fill in the connection information or if the client will should just connect to local host automatically
def host_check():                                                               
    check_input = input(str("Y/N: "))                                           #input for yes or no

    #If it is yes it will wait for input from user and use that to connect                                       
    if check_input == "Y":                                                      
        print("Choose the host ip address: ")
        host_input = input(str("IP address: "))                                 
        port_q.put(host_input)                                                  
 
        print("Choose the host port: ")
        port_input = int (input(str("Port: ")))                                
        port_q.put(port_input)    
    #If it is no it will set all data to these predefined variables                                              
    elif check_input == "N":                                                    
        print("Set host to localhost and port to 5000")
        host = "127.0.0.1"                                                      
        port = 5000                                                             
        host_q.put(host)                                                       
        port_q.put(port)                                                        
    else:                                                                       #If the user types something else. It will ask agian.                                                     
        print("Please enter either Y or N")
        host_check()


host_check()                                                              

#Gets their values from the queues
host = host_q.get()                                                             
port = port_q.get()                                                             

print("Starting Server...")
server_socket.bind((host, port))                                                #Sets the serves host address as the defined host and port values       


#Listen thread for listening for new connections it does this by using a will loop
#When a connection is made i puts all that info into some different lists
#Then it unpauses another bit of code
def new_connection():                                                           
    while True:                                                                 
        server_socket.listen()                                                  
        conn, addr = server_socket.accept()                                           #Accepts the connetion and defines the variable
        send_names = str(name_list)
        conn.send(send_names.encode())
        conned = "Connected to the Server!"                                     
        conn.send(conned.encode())                                              
        client_list.append(conn)                                                
        msg_list.append(conn)
        name = conn.recv(1024).decode()                                         #Recives the name
        name_list.append(name)
        name_q.put(name)                                                        
        conn_q.put(conn)                                                        
        wait_for_connection.set()                                               #Unpause a part of the code in the threadstarter. This startes a message recives thread specifed for the new client


#Waits for a message from the client. Then it will broadcast it. If it fails it will remove the client from the lists and close the socekt
def receive_from_client():
    conn = conn_q.get()                                                         
    name = name_q.get()                                                         
    while True:
        try:
            message = conn.recv(1024).decode()                                  #Recvives the messages from the client
            send_message = name +": " + message                                 #Adds the nickname for the client infront of the message
            print(str(send_message))                                            #Prints the message locally on the server
            msg_list.remove(conn)
            broadcast_to_clients(send_message)                                  #"sends" the message to a different function
            msg_list.append(conn)
        except socket.error:                                                    #If the socket gets an error it will just print and break witch will exit the loop
            name_index = client_list.index(conn)
            name = name_list[name_index]
            print(str(name) + " disconnected")
            client_list.remove(conn)
            name_list.remove(name)
            msg_list.remove(conn)
            conn.close()
            break


#For-loop for all the clients in the client list
def broadcast_to_clients(message):
    for client in msg_list:                                                     
        try:
            client.send(message.encode())                                       
        except:                                                                 #If client is not in message list of the send fails it will just continue the loop
            continue


# This takes the input from the command line and checks if it a command or not. If not it will just send a message to the clients.
# Help command printes text.
# The kick command takes the name of client from an input. It will then check what index it has and use the same number in the client list.
# Then we know what client it is, and we can remove it.
# Exit command will kick all clients, then shut off 
def message_to_client():
    while True:
        user_input = input()                                                    
        if user_input == "--help":                                              #If the input is --help it will print info about all the commands
            print("List of commmands:")
            print("--kick - Select and kick an client")
            print("--exit - closes the program")
            print("If you wanna write to the users just type what ever")
            print("aslong as it doesn't match any of the commands above")
        elif user_input =="--kick":                                             #If the input is --kick will kick selected user
            print("Which of these would you like to kick?")
            print(name_list)                                                    
            print("The next line you write will kick the person")
            kick_client = input()                                               
            try:                                                                #Trys to kick that client
                name_index = name_list.index(kick_client)                       
                client = client_list[name_index]                                
                message = "--exit"
                client.send(message.encode())                                   #We send a --exit to the client so it will just shut off
                client.close()                                                  #And close out connection with the client
                client_list.remove(client)                                      
                name_list.remove(kick_client)                                    
            except:                                                             #If it doesn't work, the user just gets an error message
                print ("User not found")
                continue
        elif user_input == "--exit":                                            #If the input is --exit it will send an message to the clients and shuts them of before closing the server.
            print("Kicking all clients, and shuting down")
            message = "Server is shutting down you, will be disconnected automaticlly"
            broadcast_to_clients(message)
            message = "--exit"
            broadcast_to_clients(message)
            sleep(5)                                                            #Waits for the clients the read the message before getting shut off
            print("All clients kicked")
            print("Shuting down..")
            os._exit(1)                                                         #Shuts of the server
        else:                                                                   #If the user input is not an command it will just be sendt out as an message
            message = "Host: " + user_input
            broadcast_to_clients(message)
    
#The threadstarter / Manager for the server
#It will first start the listening thread, then the message to client, so the receive message client
def thread_starter():                                                        
    new_connection_thread = threading.Thread(target=new_connection)             
    new_connection_thread.start()                                               
                                                                                
    message_to_client_thread = threading.Thread(target=message_to_client)       
    message_to_client_thread.start()
                                                                     
    while True:                                                                 #This will create a new thread each time listening threads unpauses the event. Each client has it's own message thread
        wait_for_connection.wait()
        receive_from_client_thread = threading.Thread(target=receive_from_client)
        receive_from_client_thread.start()


thread_starter()
 

