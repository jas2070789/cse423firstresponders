import time
from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import UUID, Peripheral
import bluepy.btle
import subprocess
import socket
from datetime import datetime

#modify the following constants according to the config of the wearable
device_name = "Wearable"
device_addr = "none"
device_addr_type = "random"
device_char_handle = "Location"
device_char_UUID = 0x2A8A
char_read_interval = 1  #time inverval of reading data from the wearable, in [second]
record_size = 0

#extract the employee id from the received string
def get_employee_id(str):
    str_elements = str.split('|')
    return str_elements[0]

#extract the packet id from the received string
def get_packet_id(str):
    str_elements = str.split('|')
    return str_elements[1]

#extract the quad number from the received string
def get_quad_number(str):
    str_elements = str.split('|')
    return str_elements[2]

#extract the step count from the received string
def get_step_count(str):
    str_elements = str.split('|')
    return str_elements[3]

#get the current timestamp as a string
def get_timestamp():
    # current date and time
    now = datetime.now()

    timestamp = datetime.timestamp(now)
    dt_object = datetime.fromtimestamp(timestamp)
    time_str = dt_object.strftime('%H:%M:%S:%f')
    return time_str

#check for duplicate packet, then insert the currently received packet into database
#if database size is greater than 500 bytes, clear database and send it to central hub
def insert_record(e_id, q, s, ts, p_id):
    global record_size

    modified_record = ts + '|' + e_id + '|'+ q + '|' + s + '\n'
    #print("modified: ", modified_record)

    #store the contents of the file in a list
    f = open("result.txt", "r")
    contents = f.readlines()
    f.close()

    #print("contents read")
    #create a list of packet id
    packet_numbers = []
    i = 0
    while i < len(contents):
        #print("len:" , len(contents))
        packet_numbers.append(contents[i].split("|")[0])
        i = i + 1

    #create a list of step counts
    step_list = []
    i = 0
    while i < len(contents):
        step_list.append(contents[i].split("|")[3])
        i = i + 1

    #create a list of quad number
    quad_numbers = []
    i = 0
    while i < len(contents):
        quad_numbers.append(contents[i].split("|")[2])
        i = i + 1

    #check if the record already exists
    if any(ts in sl for sl in packet_numbers):  #packet number is the same
        record_exit = True
    else:
        record_exit = False

    #when the record is new, insert the record in the correct position
    if record_exit == False:
        
        #add new packet to the proper location
        contents.append(modified_record)        
        contents = "".join(contents)
        record_size = record_size + 1

        #update database file
        f = open("result.txt", "w")
        if(record_size > 10):   #database full, send current database to ad-hoc
            retry = 0

            while retry < 50:
                notification = "SEND"
                sock.sendto(notification.encode(), (ips, 5005))
                retry = retry +1
                
                data, addr = sock.recvfrom(1024)
                print(str(data))
                if data.decode() == "READY":
                    input("IN IF STATEMENT")
                    msg ="LOC_DATA " + str(contents)
                    sock.sendto(msg.encode(), addr)
                    
                    data, addr = sock.recvfrom(1024)
                    if data.decode() == "RECEIVED":
                        break

            #clear database
            f.write("")
            record_size = 0     #reset the number of records to zero
        else:
            f.write(contents)

        f.close()
        

#filter out dicovered devices
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleDiscovery(self, dev, new_dev, new_dat):
        if new_dev:
            pass
        if new_dat:
            pass

print("Program running")
scanner = Scanner().withDelegate(ScanDelegate())

#create an empty database file
f = open("result.txt", "w")
f.write("")
f.close()

#scan wearable devices by name
device_found = 0
while device_found == 0:
    
    devices = scanner.scan(0.35)    #start scanning
    for ii in devices:  #ii: all devices discovered
        print(ii.addr, ii.getValueText(9))
        if ii.getValueText(9) == device_name:   #target device found by name
            device_addr = ii.addr   #extract MAC addr
            device_found = 1        #exit loop

print("device found")
print("device address: ", device_addr)

#connect to device
p = Peripheral(device_addr, device_addr_type, 0)

#modify if multiple characteristics are available
ch = p.getCharacteristics(uuid = UUID('4598FB6C-F56B-4028-AD27-E3F7AA14891F'))[0]

#create a socket for notifying the central hub
ips = subprocess.check_output(['hostname', '--all-ip-addresses'])
ips = ips.strip()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#repeatedly read data from the wearable and store it into the text file
while 1:
    #get updated characteristisc value
    val = ch.read()
    print("received:" + str(val))

    #extract fields from received packet
    employee_id = get_employee_id(str(val))
    #print("Empoyee id: ", employee_id)

    packet_id = get_packet_id(str(val))
    #print("packet_id: ", packet_id)

    ts = get_timestamp()
    #print("timestamp: ", ts)

    quad = get_quad_number(str(val))
    #print("quad#: ", quad)

    step = get_step_count(str(val))
    #print("step_count: ", step)

    #check for duplicate packet, then insert the currently received packet into database
    #if database size is greater than 500 bytes, clear database and send it to central hub
    insert_record(employee_id, quad, step, ts, packet_id)
    print(ts + '|' + employee_id + '|'+ quad + '|' + step)

    #insert_record(packet_id, str(val))
    time.sleep(1)

p.disconnect()