import socket

UDP_IP = "127.0.0.1"

# IP address of client (used for initial testing)
# TODO: create a system where each client address doesn't need to be hard-coded and bound
ADHOC_IP = "10.0.0.1"

# network port to bind all communication to
UDP_PORT = 5005

# configure network socket
sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
					 
# bind socket to UDP_PORT
sock.bind((ADHOC_IP, UDP_PORT)) # this only binds 10.0.0.1 to port 5005

# set server to constantly be listening for data transmitted to the configured socket
while True:
    # receive data and IP address from sender
    data, addr = sock.recvfrom(1024)
	
    # for debug
    print "received message:", data
    
    # save corresponding transmitted data (ie, the  IP address and port of client)
    return_addr = addr[0]
    return_port = addr[1]
    
    # for debug
    print "Return address: ", str(return_addr)
    print "Return port: ", str(return_port)
    
    # return a test message to sender/client
    return_message = "I got your message."
    sock.sendto(return_message, (return_addr, return_port))
