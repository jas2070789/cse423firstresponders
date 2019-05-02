import socket
import sys
import subprocess
import time

# This python program acts as an echo client/server for sending data between
# the Ad Hoc network nodes.

# A variable to determine whether or not the system has been initialized.
initialized = False

# The numerical network_position of this device in the Ad Hoc network. A smaller number indicates
# that it's closer to the Central Hub.
network_position = None

# This list signifies the neighbors that this device interacts with.
neighboring_devices = []

# The times of the neighboring devices. Get the device with the shortest time to ping.
neighboring_times = []

# This list represents the primary device this node will route data to.
send_to_device = []

# This list represents the primary device this node will receive data from.
receive_from_device = []

# The max amount of supported addresses.
supported_address_count = 16

# The max amount of devices this device can send to. Left as one for simplicity.
MAX_SEND_DEVICE = 1

# The max amount of devices this device can receive from. Left as one for simplicity.
MAX_RECEIVE_DEVICE = 1

# This variable represents this device's IP address.
this_IP_address = ""

UDP_PORT = 5005

# First we need to get the device's IP address.
def get_ip_address():
    ips = subprocess.check_output(['hostname', '--all-ip-addresses'])
    return ips

def wait_for_initialization():
    global initialized
    global network_position
    while not initialized:
        print "Awaiting initialization command from nearby device or the Central Hub."
        
        # Attempt to retrieve an ASSIGN command from a neighboring device.
        data, addr = sock.recvfrom(1024)
        
        print type(data)
        print str(data)
        
        # We can get the device address out of the recvfrom command to save the IP
        # of the device that sent data to this one.
        print "Data retrieved from nearby device."
        print "Device address: %s\n" % str(addr)
        
        # Processes an ASSIGN command and gives the device a numerical position value.
        if "ASSIGN" in data:
            # This is the position of the number that signifies the device from the Hub.
            device_position = data[len(data) - 1]
            try:
                network_position = int(device_position)
                print str(network_position)
                
                # Set initialized to true to break out of the loop.
                initialized = True
                
                # This now becomes the device that we're going to send data to. 
                send_to_device.append(addr[0])
                
                # Send back a confirmation message to the original device.
                MESSAGE = "ASSIGN COMMAND RECEIVED."
                sock.sendto(MESSAGE, (addr[0], addr[1]))
            except:
                MESSAGE = "INIT FAIL"
                sock.sendto(MESSAGE, (addr[0], addr[1]))
                print str(device_position)
                initialized = False
        elif "CHECK" in data:
            # We're still trying to initialize this device, so say that the device isn't initialized yet and is viable for assigning.
            MESSAGE = "INVALID INIT"
            sock.sendto(MESSAGE, (addr[0], addr[1]))
            initialized = False
        else:
            print "This device is not yet initialized. Waiting for an ASSIGN command from a neighboring device."
    return True

# After the device has been initialized, locate other neighbors to get the device that this node will get data from.
# The problem I can foresee is that we will need to check to see if that object already has been assigned a value
# in the network to avoid duplication. That means this method is only suitable for finding neighbors and nothing else.
# Should we make it like... when a device is being initialized, check to see if its already been initialized, and if it says
# no, THEN we can send an assign command? This should also be towards the device closest to the current device.
def find_neighbors():
    # This code is reltively similar to the find_neighbors() function on the Central Hub.
    # Issue the CHECK command to see if that device is already initialized.
    
    position = 1
    
    while position <= supported_address_count: # WHILE position <= 16
        current_IP = '10.0.2.'
        
        # Boolean to determine whether or not a device is there.
        is_there = False
        
        # Concatenate string with position variable for ping.
        current_IP += str(position)
        
        # Print the current IP for debugging.
        print("Current IP Address: " + str(current_IP))
        
        # Specify the max amount of times we're allowed to retry pinging.
        max_retries = 3
        retry_count = 0
        
        while current_IP != "10.0.2.15" and retry_count < max_retries and current_IP != this_IP_address and current_IP not in send_to_device:
            try:
                call_output = subprocess.check_output(['ping', '-c', '1', current_IP])
                print "ping output: " + str(call_output)
                is_there = True
                break
            except:
                print "Could not detect nearby host with this IP."
            
            if not is_there:
                retry_count += 1
        
        position+=1
    
        # If we've detected an IP, add it to the neighbor and time list for later processing. Don't bother adding
        # the current device or the device that this node is already assigned to.
        # Might check this with the loop back address? Probably not a good idea, would need to check with the PI 0s.
        if is_there:
            print("IP device found successfully. Adding to neighbor list...")
            neighboring_devices.append(current_IP)
            time_index = call_output.find("time=")
            end_index = time_index + 10
            
            p_time = call_output[time_index:end_index]
            
            p_time = p_time[5:]
            
            #Append the neighbor time to the list. This will coincide with the
            #element in the neighbor list.
            neighboring_times.append(p_time)
            
            print(current_IP + " added to the neighboring devices list.")
            
def init_new_devices():
    # Now we have the neighboring device list filled with neighboring IPs. Take those IPs, find the closest nodes,
    # and send ASSIGN commands to those nodes. A check will be given with each of these nodes to make sure they aren't
    # already initialized.
    while len(receive_from_device) < MAX_RECEIVE_DEVICE and len(neighboring_devices) > 0 and len(neighboring_times) > 0:
        
        # Use the neighboring times array to figure out which device is closest to this one.
        smallest_time = min(neighboring_times)
        
        smallest_time_index = neighboring_times.index(smallest_time)
        
        potential_neighbor = neighboring_devices[smallest_time_index]
        
        # Send a CHECK command to this neighbor to see if it's already been initialized or not.
        MESSAGE = "CHECK"
        sock.sendto(MESSAGE, (potential_neighbor, UDP_PORT))
        
        # Get the return message from the device to make sure that it hasn't been initialized.
        data, addr = sock.recvfrom(1024)
        
        # The device has not yet been initialized. We can receive data from this device.
        if data == "INVALID INIT":
            
            # Get the network position for the new device.
            new_device_position = network_position + 1
            
            # Generate the ASSIGN message.
            MESSAGE = "ASSIGN " + str(new_device_position)
            
            # Keep trying to send the assign command to the new device until it complies or times out.
            max_retries = 10
            retry_count = 0
            while(retry_count < max_retries):
            
                print("Sending ASSIGN command to new device...")
                # Send the ASSIGN command to the new device.
                sock.sendto(MESSAGE, (potential_neighbor, UDP_PORT))
            
                print("ASSIGN command sent. Waiting for response from device...")
                # Get confirmation message from device.
                data, addr = sock.recvfrom(1024)
            
                if data == "ASSIGN COMMAND RECEIVED.":
                    print("Initialization of new device successful.")
                    receive_from_device.append(potential_neighbor)
                    neighboring_devices.remove(potential_neighbor)
                    neighboring_times.remove(smallest_time)
                    break
                
                time.sleep(2)
                retry_count += 1
                
        # The device has already been initialized and we don't want to assign anything else to it.
        else:
            print("Target device has already been initialized.")
            neighboring_devices.remove(potential_neighbor)
            neighboring_times.remove(smallest_time)
       
       
       # TODO:: Functionality to tell if this device is on the edge.
        
# The main server protocol for each device. Once it finishes initialization procedures, it comes here.
def main_server():
    # Sock is bound as a server address. Basically what this main server is going to do is listen for
    # incoming commands.
    
    # I would imagine we could just use recvfrom to wait for a command. It stalls until it gets one. Michael
    # will have his BLE stuff running in a different window, and it will send a done command when it finishes
    # processing.
    
    # The end device will not have a device that it receives from. It will only send data when it receives the OK
    # from Michael's program.
    print("Beginning main server protocols.")
    
    while True:
        print("Ready to receive data from network.")
    
        # Get command.
        data, addr = sock.recvfrom(1024)
    
        # The possible commands this device can receive are:
        # ASSIGN
        # CHECK
        # SEND
        # READY
    
        # Should we send a "SEND" command to another device to prepare it, and THEN send the data? This ensures that the other device
        # actually gets the data, but it would block that device from receiving other wireless commands.
        # I think that would be a good idea to be honest.
    
        # Here though we're processing the different commands the device can receive, SEND being one of them. We will also need a way to guarantee
        # that the device will never be blocked out indefinitely. Timeouts?
    
        if data == "SEND":
            # The SEND command indicates that the device is about to be sent location data from another device. Prepare to receive
            # it and guarantee that it's been retrieved.
            print("Received send command from device...")
            MESSAGE = "READY"
            print("Device is ready to receive location data.")
            # Send the READY command back to the device and immediately open up a recvfrom command to retrieve data.
            sock.sendto(MESSAGE, addr)
            
            retrieved_comm = False
            
            # Keep trying to retrieve data until abandon command is received.
            while not retrieved_comm:
                print("Trying to retrieve data...")
                
                # Retrieve data from device.
                data, addr = sock.recvfrom(1024)
            
                print("Transmission retrieved from device.")
        
                input(str(data))
                
                if "LOC_DATA" in data:
                    # We got the data. Send a notification back to the sending device that we got it.
                    print("Location data retrieved. Sending confirmation message to sender...")
                    MESSAGE = "RECEIVED"
                    sock.sendto(MESSAGE, addr)
            
                    loc_data = data
            
                    # We have the location data to forward along. Send it to the next device.
                    # Get the IP of the next device.
                    send_ip = send_to_device[0]
            
                    print("Sending location data to next device in network...")
            
                    max_retries = 5
                    retry_count = 0
            
                    # Boolean to signify whether or not the device is setup.
                    device_setup = False
            
                    # While we haven't reached the retry count for sending data...
                    while retry_count < max_retries:
            
                        setup_retry = 0
                        
                        while setup_retry < 5 and device_setup:
                            # Need to set up new device for sending.
                            print("Setting up device for sending.")
                            MESSAGE = "SEND"
                            sock.sendto(MESSAGE, (send_ip, UDP_PORT))
                
                            # Ensure that we get a ready message.
                            data, addr = sock.recvfrom(1024)
                            if data == "READY":
                                print("Receiving device is ready for transmission.")
                                device_setup=True
                    
                            else:
                                print("Device transmission error. Retrying.")
                                time.sleep(1)
                                setup_retry += 1
                        
                        if setup_retry == 5:
                            print("Abandoning sending protocol.")
                            retry_count = max_retries
                            break # while retry_count < max_retries
                        # Send the device data to the next node in the network.
                        sock.sendto(loc_data, (send_ip, UDP_PORT))
            
                        print("Waiting for confirmation from receiving device...")
                        # Get a confirmation message from the device.
                        data, addr = sock.recvfrom(1024)
            
                        if data == "RECEIVED":
                            print("Data transmitted successfully. Cycling to beginning of loop.")
                            retrieved_comm = True
                            break # while retry_count < max_retries
                
                        elif data == "INVALID TRANSMISSION":
                            print("Device received invalid data. Trying to send again.")
                            time.sleep(1)
                            retry_count += 1
                    
                    if retry_count == max_retries:
                        print("Unrecoverable error has occurred. Abandon current transmission.")
                        MESSAGE = "ABANDON"
                        sock.sendto(MESSAGE, (send_ip, UDP_PORT))
                        retrieved_comm = True
                        break # while not retrieved_comm
            
                elif data == "ABANDON":
                    print("Abandoning current receiving protocol...")
                    break # while not retrieved_comm
                
                else:
                    print("Retrieved invalid location data. Telling other device to wait.")
                    MESSAGE = "INVALID TRANSMISSION"
                    sock.sendto(MESSAGE, addr)
    
        else:
            print("SEND command not properly received. Reply with INVALID TRANSMISSION.")
            MESSAGE = "INVALID TRANSMISSION"
            sock.sendto(MESSAGE, addr)
            
        
    # END OF MAIN WHILE LOOP  

if __name__ == "__main__":
    UDP_PORT = 5005
    this_IP_address = get_ip_address()
    this_IP_address = this_IP_address.strip()
    
    print str(this_IP_address)
    
    # Now that we have the device IP, we need to set up the socket for the device
    # so it can start receiving installation commands.
    
    print "Configuring Ad Hoc socket for this device..."
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((this_IP_address, UDP_PORT))
    # Set a timeout of 5 seconds to avoid indefinitely waiting.
    #sock.settimeout(5)
    
    print "Socket configured for this device."
    
    success = False
 
    success = wait_for_initialization()
    
    find_neighbors()
    
    # If we were able to initialize the device correctly, now we need to scan for other devices. Uses similar methodology to Central Hub scanning.
    if(success) and len(neighboring_devices) > 0:
        init_new_devices()
    
    # Once we initialize new devices to send to this one... then what?
    # Is the server going to be running in its own terminal?
    # So  I think that the server can be run in this program as well after everything gets initialized.
    main_server()
        
    sys.exit(0)