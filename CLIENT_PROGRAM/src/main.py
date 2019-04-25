# Created by Patrick Archer on 15 April 2019

"""
@file is the main script that the Client will run to query data from the Central Hub.
"""

"""========== IMPORTS =========="""

import sys
from FirstResponder_struct import firstResponder
import json
import socket
import subprocess
from sqlite3 import Error

"""========== GLOBAL VARS =========="""

# IP of the CH
UDP_IP_HUB = "10.0.2.1"   # real IP address of CH
# UDP_IP_HUB = "10.0.2.16"    # for testing purposes
#UDP_IP_HUB = subprocess.check_output(['hostname', '--all-ip-addresses']).strip()    # for testing purposes

# # DEBUG
# print(UDP_IP_HUB)

# IP of the Client device
UDP_IP_CLIENT = "10.0.2.255"   # real IP address of Client device
# UDP_IP_CLIENT = "10.0.2.15"     # for testing purposes

# network port for all communication between CH and other nodes
UDP_PORT = 5005

"""========== MAIN() =========="""

def main():

    # display main menu contents and get user's desired cmd selection
    user_cmd = mainMenu()

    # execute corresponding functions depending on user's cmd selection
    mainMenuSelection(user_cmd)

"""========== ADDITIONAL FUNCTIONS =========="""

# displays main menu content to user
def mainMenu():

    # # DEBUG: create initial firstResponder object to test valid OOP configuration
    # fr1 = firstResponder('001', 'A1', 'F1')
    # print("[CONSOLE] Initial: ", fr1.uuid)
    # fr1.changeClosestAnchor('A2')
    # print("[CONSOLE] Change CA to A2: ", fr1.closest_anchor)
    # fr1.changeCurrentFloor('F3')
    # print("[CONSOLE] Change CF to F2: ", fr1.current_floor)

    print("\n\t======== MAIN MENU ========")
    userCMD = input("""
    Please enter a cmd and press return.
    0 - Quit Program
    1 - Get all current location data of active beacons
    2 - temporary_cmd_2
    \n""")

    # # DEBUG
    # print("[CONSOLE] Entered user cmd: ", userCMD)

    return userCMD

# handles what is to be executed depending on what cmd the user selected from the main menu
def mainMenuSelection(cmd):

    # # DEBUG
    # print("mainMenuSelection.cmd = ", cmd)

    # if cmd == 0 (quit), terminate program
    if cmd == '0':
        sys.exit("\n[CONSOLE] Exit command registered. Terminating program now.")
    # if cmd == 1 (getAllLocations), begin protocol to get all current location datas of active beacons
    elif cmd == '1':
        print("\n[CONSOLE] Beginning execution of getAllLocations().")
        getAllLocations()
    # if cmd == 2 (cmd2), begin protocol to carry out desired functionality
    elif cmd == '2':
        print("\n[CONSOLE] Placeholder: Beginning execution of protocol_cmd2().")
        protocol_cmd2()
    # if cmd is unknown or invalid, catch error and re-execute main()
    else:
        print("\n[CONSOLE] Invalid command entered. Please try again.")
        main()

# handles functionality to query all current location data from Hub and display results to user
# NOTE: make sure client is connected to WADHOC network before trying to execute queries
def getAllLocations():

    # TODO
    """
        1) Parse returned data and display to user
        2) Socket binding: Special cases and error checking
        
        * check for errors when making network connections
        * take note of special cases regarding the existence of data on the Hub
    """

    # cmd to query all current location data from CH
    cmd = "QUERYALL"
    # fully built transmission string to be sent to CH via network socket
    # transmission = cmd + "|" + UDP_IP_HUB + "|"
    transmission = UDP_IP_HUB + "|" + cmd

    # configure network socket and bind the socket to the CH IP and listening port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP_CLIENT, UDP_PORT))

    # # DEBUG
    # print(transmission)

    # send transmission to CH
    print("[CONSOLE]: Now sending transmission to Hub.")
    sock.sendto(transmission, (UDP_IP_HUB, UDP_PORT))
    # wait to receive transmission from CH
    print("[CONSOLE]: Now listening for transmissions.")
    data, addr = sock.recvfrom(1024)

    # save data, IP, and PORT to vars
    queryResults = [data, addr[0], addr[1]]  # sender_DATA, sender_IP, sender_PORT

    # DEBUG
    print(queryResults)
    # "data"
    print(queryResults[0])
    # "addr[0]"
    print(queryResults[1])
    # "addr[1]"
    print(queryResults[2])

    # DEBUG: load data (queryResults[0]) into json parser & store returned result
    try:
        tmp = json.loads(json.dumps(queryResults[0]))
        print(tmp)
    except Error as e:
        print("[CONSOLE] ERROR: ", e)

    # print(tmp["some_anchor_id"])

    # TODO: Parse data (JSON?) and store subdatas to local vars
    # TODO: Display now-localized data to user via terminal

    # call main() to keep program running and bring user back to main menu
    main()

# handles mainMenu.cmd2 functionality
def protocol_cmd2():

    # TODO
    """
        1) ...
    """

    # call main() to keep program running and bring user back to main menu
    main()

"""========== SCOPE =========="""

if __name__ == '__main__':
    main()

"""========== /\ END OF FILE /\ =========="""
