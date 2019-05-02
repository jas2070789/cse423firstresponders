# Created by Patrick Archer on 15 April 2019

"""
@file is the main script that the Central Hub will run to initially operate.
"""

"""========== IMPORTS =========="""

import sys
import json
import sqlite3
from sqlite3 import Error
import socket
import subprocess

"""========== GLOBAL VARS =========="""

# path to location database file in persistent memory
pathToDB = "database/locations.db"

# IP of the CH
# UDP_IP_HUB = "10.0.2.1"   # real IPv4 address of CH
UDP_IP_HUB = "10.0.2.15"    # for testing purposes
# UDP_IP_HUB = subprocess.check_output(['hostname', '--all-ip-addresses']).strip()    # for testing purposes

# IP of the Client device
# UDP_IP_CLIENT = "10.0.2.255"   # real IPv4 address of Client device
UDP_IP_CLIENT = "10.0.2.255"     # for testing purposes

# network port for all communication between CH and other nodes
UDP_PORT = 5005

"""========================INITIALIZATION VARIABLES=========================="""

# These variables are used to initialize the AD HOC network.
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
max_neighbors = 1

# The supported address count for the Ad Hoc Network.
supported_address_count = 16

# This device's ip address.
this_ip_address = ""

"""========== MAIN() =========="""

def main():

    # DEBUG: run testDB() to demo db functionality
    # print(testDB())
    # while True:
    #     pass

    # configure network socket and bind the socket to the CH IP and listening port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP_HUB, UDP_PORT))
    
    # Set a timeout of five seconds to avoid indefinitely waiting.
    #sock.settimeout(5)
    
    # perform initial device setup
    setup(sock)    

    # continuously repeat process of listening for a transmission then doing stuff with data from that trans.
    while True:

        # wait here to receive message from node
        print("[CONSOLE]: Now listening for transmissions.")
        data, addr = sock.recvfrom(1024)

        # >> once a msg is received from a node, react accordingly and return to listening ASAP

        print(str(addr))

        # if transmission is from the Client, treat as query communication
        if addr[0] == UDP_IP_CLIENT:
            # >> split incoming transmission into delimited parts; store data accordingly

            # >> Client Transmission Structure:  IP_ADDR | CMD

            # split transmitted string according to delimiter char ("|") & strip of unnecessary chars (spaces, etc.)
            splitTransmission = data.split('|')
            # save 1st delimited segment (Client IP address) into client_ipAddr
            client_ipAddr = splitTransmission[0]
            # save 2nd delimited segment (Client command) into client_cmd
            client_cmd = splitTransmission[1]

            # if transmission is from Client (redundant check) and the cmd == query entire location database
            if client_ipAddr == UDP_IP_CLIENT and client_cmd == "QUERYALL":
                # perform a complete database query and save the fetchResults into results_dbQueryAll
                results_dbQueryAll = dbQueryAll()

                # DEBUG
                print(results_dbQueryAll)

                # now that query results are fetched, send results back to Client
                sock.sendto(str(results_dbQueryAll), (UDP_IP_CLIENT, UDP_PORT))
                #sock.sendto(str(results_dbQueryAll), addr)
            else:
                print("[CONSOLE]: ERROR: Invalid command received. Dropping transmission.")

        # if transmission is from anything else besides the Client, treat as Anchor communication
        else:
            loc_data = ""
            if data == "SEND":
                sender_IP = addr[0]
                # Device wants to send data to this device. Notify that we're ready.
                print("[CONSOLE]: Device IP: " + sender_IP + " wants to send data to this device.")
                MESSAGE = "READY"
                
                sock.sendto(MESSAGE, addr)
                
                print("[CONSOLE]: Ready to retrieve data from " + sender_IP)
                
                # Keeps track of whether or not this Hub retrieved the right data.
                data_retrieved = False
                
                while not data_retrieved:
                    data, addr = sock.recvfrom(1024)
                
                    if data == "ABANDON":
                        print("[CONSOLE]: Uncorrectable error during data transmission. Abandoning this send sequence.")
                        break
                
                    sender_IP_2nd = addr[0]
                
                    print("[CONSOLE]: Received transmission from " + sender_IP_2nd)
                
                    if sender_IP_2nd != sender_IP:
                        print("[CONSOLE]: Did not expect data from this device. Trying again.")
                        MESSAGE = "WAIT"
                        sock.sendto(MESSAGE, addr)
                    else:
                        # Check to make sure that we got the data.
                        if "LOC_DATA" in data:
                            print("[CONSOLE]: Received location data and saving to database.")
                        
                            # Take LOC_DATA out of the string and pass it along to be parsed by the database.
                            loc_data = data[9:]
                        
                            # Send confirmation message to device.
                            MESSAGE = "RECEIVED"
                            sock.sendto(MESSAGE, addr)
                            
                            data_retrieved = True
                        else:
                            # Incorrect data was retrieved. Have the original device resend.
                            print("[CONSOLE]: Incorrect data retrieved.")
                            MESSAGE = "INVALID TRANSMISSION"
                            sock.sendto(MESSAGE, addr)
                
            # >> Parse transmission, consistently validly extract data, save to database
            # >> Anchor Transmission Structure:  TIMESTAMP | ID | QUAD | STEPS

            if loc_data != "":

                for index in loc_data:

                    # split transmitted string according to delimiter char ("|") & strip of unnecessary chars (spaces, etc.)
                    splitTransmission = index.strip().split('|')
                    # save 1st delimited segment (transmission timestamp) into node_timestamp
                    node_timestamp = splitTransmission[0]
                    # save 2nd delimited segment (employeeID/wearableID/beaconID) into node_id
                    node_id = splitTransmission[1]
                    # save 3rd delimited segment (quadrant #) into node_quad
                    node_quad = splitTransmission[2]
                    # save 4th delimited segment (step count) into node_steps
                    node_steps = splitTransmission[3]

                    # >> now that the transmission has been parsed, perform database operations

                    results_dbInsertOrUpdate = dbInsertOrUpdate(node_timestamp, node_id, node_quad, node_steps)

                    # print(str(loc_data))
                    print(str(results_dbInsertOrUpdate))
                
                # send results back to node
                #sock.sendto(str(results_dbInsertOrUpdate), (UDP_IP_CLIENT, UDP_PORT))

    # # try connecting to database file and attaching a cursor
    # try:
    #     # "Open an active connection to the database file, as alias 'conn', then do ___ and close the connection."
    #     with sqlite3.connect(pathToDB) as conn:
    #         conn.row_factory = dict_factory
    #         curs = conn.cursor()
    #
    #         """DEBUG: test json parsing functionality"""
    #         results = testDB(curs)
    #         conn.commit()
    #
    #         # convert returned data into a JSON dictionary
    #         y = json.loads(json.dumps(results))
    #         print(y)
    #
    #         # print(results)
    #         # print(json.dumps(results))
    #         # print(y[0])
    #         # print(y[0]["num1"])
    #
    #         # parse returned data; if value stored in num1 == 78.38, return corresponding str1 value
    #         tmpVal = 69
    #         for i in y:
    #             print(i, i["num1"], " ", i["num2"], " ", i["str1"])
    #             if i["num1"] == tmpVal:
    #                 print(i["str1"], "contains the value", tmpVal)
    #         """END DEBUG"""
    #
    # except Error as e:
    #     print("[CONSOLE] Error: ", e)

"""========== ADDITIONAL FUNCTIONS =========="""

# perform initial boot device setup procedures
def setup(sock):
    global this_ip_address
    
    print("Beginning AD HOC NETWORK Initialization...")

    # Get the ip address of this device and strip the endline character.
    this_ip_address = get_ip_address()
    this_ip_address = this_ip_address.strip()

    print (this_ip_address)

    find_neighbors()

    print (str(found_neighbors))

    distance()

    print (str(assigned_neighbors))
    
    # Send ASSIGN commands to each device in the assigned_neighbors list.
    for item in assigned_neighbors:
        
        # Attempt to initialize the target device up to a maximum of 10 times.
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            MESSAGE = "ASSIGN 1"
            sock.sendto(MESSAGE, (item, UDP_PORT))
        
            data, addr = sock.recvfrom(1024)
        
            if data == "ASSIGN COMMAND RECEIVED.":
                print("Initialization of device " + str(item) + " successful.")
                break
            else:
                print(str(data))
                print("Could not initialize this device.")
            
            retry_count += 1

# query database for all location records
def dbQueryAll():

    # try connecting to database file and attaching a cursor
    try:
        # "Open an active connection to the database file, as alias 'conn', then do ___ and close the connection."
        with sqlite3.connect(pathToDB) as conn:

            # reconfigure row_factory to export as a json dict.
            conn.row_factory = dict_factory
            # create database cursor
            curs = conn.cursor()

            # SQL: select every beacon/UUID & corresponding data
            curs.execute("SELECT * FROM locations")

            # # commit cursor executions and return fetch results
            # conn.commit()
            # fetchResults = json.loads(json.dumps(curs.fetchall()))
            # # print(fetchResults)
            # return fetchResults

            return json.loads(json.dumps(curs.fetchall()))

    except Error as e:
        print("[CONSOLE] ERROR: ", e)

#
def dbInsertOrUpdate(node_timestamp, node_id, node_quad, node_steps):

    # try connecting to database file and attaching a cursor
    try:
        # "Open an active connection to the database file, as alias 'conn', then do ___ and close the connection."
        with sqlite3.connect(pathToDB) as conn:

            # reconfigure row_factory to export as a json dict.
            conn.row_factory = dict_factory
            # create database cursor
            curs = conn.cursor()

            # SQL: if table exists, either insert or update row (depending on if data exists already or not)

            # >> The following c.exec will only run with a SQLite version of 3.24.0 or higher
            # If an entry does not already exist with the node_id, create a new entry in the locations table.
            # If an entry does already exist with the node_id, update the current entry with the new timestamp, quad, and steps.
            curs.execute("INSERT INTO locations (timestamp, id, quad, steps)"
                         "VALUES ("+str(node_timestamp)+", "+str(node_id)+", "+str(node_quad)+", "+str(node_steps)+")"
                         "ON CONFLICT(id) DO UPDATE"
                         "SET timestamp="+str(node_timestamp)+", quad="+str(node_quad)+", steps="+str(node_steps)+"")

            # DEPRECATED; does not accomplish desired functionality
            # curs.execute("INSERT OR REPLACE INTO locations (timestamp, id, quad, steps) "
            #              "VALUES ("+node_timestamp+", (SELECT * FROM locations WHERE id="+node_id+"), "+node_quad+", "+node_steps+")")

            conn.commit()
            curs.execute("SELECT * FROM locations")
            fetchResults = json.loads(json.dumps(curs.fetchall()))
            return fetchResults
    except Error as e:
        print("[CONSOLE] ERROR: ", e)

# DEBUG: create some fake table and do stuff w/ it in SQL (technically sqlite3)
def testDB():

    tmpNUM1 = 404
    tmpNUM2 = 96
    tmpSTR1 = "row3_UPSERT"

    conn = sqlite3.connect(pathToDB)
    cursor = conn.cursor()

    # do a bunch of random SQL commands to test functionality
    cursor.execute("DROP TABLE IF EXISTS test")

    cursor.execute("CREATE TABLE test"
                   "(num1 VALUE, num2 INTEGER, str1 TEXT)")

    cursor.execute("INSERT INTO test (num1, num2, str1)"
                   "VALUES (25.2, 10, 'row1')")

    cursor.execute("INSERT INTO test (num1, num2, str1)"
                   "VALUES (78.38, 55, 'row2')")

    cursor.execute("INSERT INTO test (num1, num2, str1)"
                   "VALUES (100, 84, 'row3')")

    cursor.execute("UPDATE test SET num1 = 69, num2 = 96, str1 = 'newRow3' WHERE str1 == 'row3'")

    # cursor.execute("INSERT OR REPLACE INTO test (num1, num2, str1) "
    #                "VALUES ("+str(tmpNUM1)+", (SELECT num2 FROM test WHERE num2="+str(tmpNUM2)+"), "+str(tmpSTR1)+")")

    cursor.execute("DELETE FROM test WHERE str1=='row2'")

    # fetch data from the table and return
    cursor.execute("SELECT * FROM test")
    # cursor.execute("SELECT * FROM test WHERE str1=='row2'")
    # fetch = cursor.fetchall()
    # return fetch
    return cursor.fetchall()

# DO NOT ALTER: used to generate JSON-formatted data from database queries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

"""=================================INITIALIZATION FUNCTIONS==============================="""

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
        # print current_IP
        
        # Specify the maximum amount of times we're allowed to retry pinging as well as initialize the retry_count.
        max_retries = 3
        retry_count = 0
            
        # While we haven't retried enough times yet, ping for nearby devices up to the max amount of supported devices.
        while retry_count < max_retries and current_IP != this_ip_address: 
            try:
                call_output = subprocess.check_output(['ping', '-c', '1', current_IP])
                print ("ping output: " + str(call_output))
                is_there = True
                break
            except:
                print ("Could not detect nearby host with this IP.")
            
            if not is_there:            
                retry_count += 1    
        
        position+=1
        
        # If we found a device, record its IP address and the time it took to communicate with that address. The devices
        # with the shortest time to communicate are the devices the Central Hub will primarily interact with.
        if is_there:
            print ("IP address found successfully. Updating List.")
            found_neighbors.append(current_IP)
            time_index = call_output.find("time=")
            end_index = time_index + 10

            p_time = call_output[time_index:end_index]
            
            p_time = p_time[5:]

            # Append the neighbor time to the list. This will coincide with the
            # element in the neighbor list.
            neighbor_times.append(p_time)           

            print (current_IP + " added to the found_neighbors list.")

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
        
        print ("IP Device " + str(assigned_device) + " assigned to this device.")

"""========== SCOPE =========="""

if __name__ == '__main__':
    main()

"""========== \/ @file END \/ =========="""
