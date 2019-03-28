import socket
import sys

# IP of the client
UDP_IP = "127.0.0.1"

# network port to bind all communication to
UDP_PORT = 5005

# test message to be sent to server (for initial debugging)
MESSAGE = "Hello, World!"

# for debug
print "UDP IP:", UDP_IP
print "UDP Target Port:", UDP_PORT
print "Message:", MESSAGE

# configure network socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send test message to server
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

# receive reply message from server
data, addr = sock.recvfrom(1024)
print(str(data))