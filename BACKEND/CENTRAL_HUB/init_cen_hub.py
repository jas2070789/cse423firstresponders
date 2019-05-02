import sys
import socket
import subprocess

# The array of found neighboring devices detected through the subprocess.check_call command.
found_neighbors = []

# The times of the discovered neighbors.
neighbor_times = []

# The assigned_neighbors that this hub will interact with.
assigned_neighbors = []

# The times of the assigned_neighbors
assigned_times = []

# The maximum amount of neighbors this device is allowed to have and interact with
# For all devices except the Hub, it's 2. 
# The Hub bases its neighbors solely on distance, since it is what initializes the network.
max_neighbors = 4

# The supported address count for the Ad Hoc Network.
supported_address_count = 16

# This device's ip address.
this_ip_address = ""

# Return the IP address of this device.
def get_ip_address():
    ips = subprocess.check_output(['hostname', '--all-ip-addresses'])   
    return ips

def find_neighbors():
    # Start checking for other devices. We can support up to 32 IP addresses, so we will loop
    # through pinging for each IP address and storing neighbors in a list.

    # Unfortunately, this method is not very fast as we have to iterate through a large list of IPs
    # and ping them several times. Optimizations are being looked at.
    position = 1
    
    while position <= supported_address_count: # WHILE position <= 16
        current_IP = '10.0.2.'
        
        # Boolean to keep track of whether or not an individual device was found or not.
        is_there = False
        # Concatenate string with position variable.
        current_IP += str(position)
        
        # Print the current_IP for debugging.
        print current_IP
        
        # Specify the maximum amount of times we're allowed to retry pinging as well as initialize the retry_count.
        max_retries = 3
        retry_count = 0
            
        # While we haven't retried enough times yet, ping for nearby devices up to the max amount of supported devices.
        while retry_count < max_retries: 
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
        
        # If we found a device, record its IP address and the time it took to communicate with that address. The devices
        # with the shortest time to communicate are the devices the Central Hub will primarily interact with.
        if is_there and current_IP != this_ip_address:
            print "IP address found successfully. Updating List."
            found_neighbors.append(current_IP)
            time_index = call_output.find("time=")
            end_index = time_index + 10

            p_time = call_output[time_index:end_index]
            
            p_time = p_time[5:]

            # Append the neighbor time to the list. This will coincide with the
            # element in the neighbor list.
            neighbor_times.append(p_time)           

            print current_IP + " added to the found_neighbors list."
    

def distance():
    
    while len(assigned_neighbors) < max_neighbors and len(neighbor_times) > 0 and len(found_neighbors) > 0:
        # Use the neighbor times array to figure out what devices are closest to the Central Hub, and designate
        # those devices as the first step in the network. We first need to get the lowest time currently present
        # in the list.
        smallest_time = min(neighbor_times)
        
        # With the smallest_time, return the index of that time from the neighbor_times array so we can get the 
        # device IP associated with that time.
        smallest_time_index = neighbor_times.index(smallest_time)

        # Now use that smallest_time to get the device IP from the found_neighbors array.
        assigned_device = found_neighbors[smallest_time_index]
        
        # Append the assigned_device IP to the assigned_neighbors array.
        assigned_neighbors.append(assigned_device)

        # Append the smallest_time to the assigned_times array.
        assigned_times.append(smallest_time)

        # Delete the neighbor from the found_neighbors list.
        found_neighbors.remove(assigned_device)

        # Remove the smallest time from the neighbor_times list so we can later get the next shortest time.
        neighbor_times.remove(smallest_time)
        
        print "IP Device " + str(assigned_device) + " assigned to this device."
    

if __name__ == "__main__":
    print("Beginning AD HOC NETWORK Initialization...")

    # Get the ip address of this device and strip the endline character.
    this_ip_address = get_ip_address()
    this_ip_address = this_ip_address.strip()

    print this_ip_address

    find_neighbors()

    print str(found_neighbors)

    distance()

    print str(assigned_neighbors)

    assigned_neighbors.append("10.0.2.15")
    assigned_neighbors.append("10.0.2.14")
    assigned_times.append("0.245")
    assigned_times.append("0.756")

    # Save the neighbor information in a file to be accessed by the server and client programs.
    neighbor_file = open("neighbors.txt", "w")
    for item in assigned_neighbors:
        neighbor_file.write("%s\n" % item)
    neighbor_file.close()

    time_file = open("times.txt", "w")
    for item in assigned_times:
        time_file.write("%s\n" % item)
    time_file.close()
    

    
    


