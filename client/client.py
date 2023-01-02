import os
import re
import threading
import socket
from time import sleep
from queue import Queue

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                       #Creates the Client socket
                                                                                      
host_q = Queue()                                                                                        #Queue for host info
port_q = Queue()                                                                                        #Queue for port info
name_q = Queue()                                                                                        #Queue for name
word_q = Queue()                                                                                        #Queue for word

print("Welcome to S354418's chatroom client")
print("If you need any help just do --help")


#The check function. Checks if the user wants to fill in the connection information or if the client will should just connect to local host automatically
def host_check():                                                                                      
    print("Do you wanna set the connection info to the server(Y)?") 
    print("If not it will be satt automatically connect to the server by localhost(N)")
    check_input = input(str("Y/N: "))                                                                   #input for yes or no

    #If it is yes it will wait for input from user and use that to connect
    if check_input == "Y":                                                                              
        print("Choose the host ip address: ")
        host_input = input(str("IP address: "))                                                         
        host_q.put(host_input)      

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
    else:                                                                                               #If the user types something else. It will ask agian.
        print("Please enter either Y or N")
        host_check()


host_check()                                                                                            

#Gets their values from the queues
host = host_q.get()                                                                                     
port = port_q.get()                                                                                     

client_socket.connect((host, port))                                                                     #Connects to the specifed address and port.

name_list = client_socket.recv(1024).decode()                                                           #Receives the list of usernames taken

print("To use the bots please input the same name as displayed below")
print("If not just select your own name")
print("Stian, Zack, Chuck and Mindy are bots")
print("These names are already in use:")
print(str(name_list))


#It will check if the username is already in use
def name_check():
    name = input("Choose your nickname : ").strip()                                                     #nickname input. The strip() removes the spaces in front and back
    if name in name_list:                                                                               
        print("Name already in use, choose a different one")
        name_check()                                                                                    
    else:
        name_q.put(name)                                                                                


name_check()                                                                                          

conned = client_socket.recv(1024).decode()                                                              #Recvives the welcome message from the server and decodes it
print(conned)

username = str(name_q.get())
name_send = client_socket.send(username.encode())                                                       #Sends the nickname to the server

#This will be one of threads in the client, this waits for an input and sends it to the server
def send_to_server():                                                                                   
    while True: 
        message_to_send = input()                                                                   
        if message_to_send == "--exit":                                                                 #If the user inputs "--exit" it will close the program
           os._exit(1)                                                                                  
        elif message_to_send =="--help":
            print("--exit - disconnects the client")
            print("If you wanna send a message just type in the command line. As long as it is not an command")
        else:                                                                                           
            client_socket.send(message_to_send.encode())                                                #Sends the message to the server

#Waits for message from the server. It will then check if it is a command. If not it will just print it
def receive_from_server():                                                                             
    while True:  
        message = client_socket.recv(1024).decode()                                                      

        if message == "--exit":                                                                         
            print("You have been kicked!")                                                              
            os._exit(1)
    
        print(message)                                                                                 
        extracted = re.findall(r'\w+', message)                                                         #It will then set the variable as a list of the different words
        word = extracted[-1]                                                                            #sets the word variable as the last word in the list 
        word_q.put(word)                                                                                

#This startes the two threads for the client code
def thread_starter():                                                                                   
    receive_from_server_thread = threading.Thread(target=receive_from_server)
    receive_from_server_thread.start()                                                                  #Starts the receive thread

    send_to_server_thread = threading.Thread(target=send_to_server)           
    send_to_server_thread.start()                                                                       #Starts the send message thread

#These functions are the bots, they take the word and send a message to the server
def stian():
    word = str(word_q.get())
    message = "Hmm. I don't know, what I think about " + str(word)+"ing"
    client_socket.send(message.encode())
    sleep(2)
    message = "Ok i'll join since Zack is coming."
    client_socket.send(message.encode())


def zack():
    word = str(word_q.get())
    sleep(1)

    if word == "exercise":                                                                              #The bot will detect if the word is a preset word and will alter it's respons
        message = "No, I can't " + str(word)+"ing, I am busy"
    else:
        message = "Yea, I could join " + str(word)+"ing."

    client_socket.send(message.encode())
    

def chuck():
    word = str(word_q.get())
    sleep(3)
    message = "I would like to " + str(word)
    client_socket.send(message.encode())


def mindy():
    word = str(word_q.get())
    sleep(4)
    message = "I don't like " + str(word)+"ing."
    client_socket.send(message.encode())

#This are basic if statements that check if the username is the same as one of the bots.
if username == "Stian":
    thread_starter()
    stian()
elif username == "Zack":
    thread_starter()
    zack()
elif username == "Chuck":
    thread_starter()
    chuck()
elif username == "Mindy":
    thread_starter()
    mindy()
else:
    thread_starter()
 

