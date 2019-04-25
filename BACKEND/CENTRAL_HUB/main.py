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
UDP_IP_HUB = "10.0.2.1"   # real IPv4 address of CH
# UDP_IP_HUB = "10.0.2.16"    # for testing purposes
# UDP_IP_HUB = subprocess.check_output(['hostname', '--all-ip-addresses']).strip()    # for testing purposes

# DEBUG
print(UDP_IP_HUB)

# IP of the Client device
UDP_IP_CLIENT = "10.0.2.255"   # real IPv4 address of Client device
# UDP_IP_CLIENT = "10.0.2.15"     # for testing purposes

# network port for all communication between CH and other nodes
UDP_PORT = 5005

"""========== MAIN() =========="""

def main():

    # perform initial device setup
    setup()

    # >> once initial setup is complete, and a valid WADHOC connection is manually verified, attach to network socket and start listening

    # configure network socket and bind the socket to the CH IP and listening port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP_HUB, UDP_PORT))

    # continuously repeat process of listening for a transmission then doing stuff with data from that trans.
    while True:

        # wait here to receive message from node
        print("[CONSOLE]: Now listening for transmissions.")
        data, addr = sock.recvfrom(1024)

        # >> once a msg is received from a node, react accordingly and return to listening ASAP

        # if transmission is from the Client, treat as query communication
        if addr[0] == UDP_IP_CLIENT:
            # >> split incoming transmission into delimited parts; store data accordingly

            # >> Client Transmission Structure:  IP_ADDR | CMD

            # split transmitted string according to delimiter char ("|") & strip of unnecessary chars (spaces, etc.)
            splitTransmission = data.strip().split('|')
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
                sock.sendto(results_dbQueryAll, (UDP_IP_CLIENT, UDP_PORT))
            else:
                print("[CONSOLE] ERROR: Invalid command received. Dropping transmission.")

        # if transmission is from anything else besides the Client, treat as Anchor communication
        else:
            # TODO: parse transmission, consistently validly extract data, save to database
            pass

            # # DEBUG
            # for index in results_dbQueryAll:
            #     print(index)

        # # for DEBUG
        # print(str(data))

        # queryResult = dbQueryAll()
        # print(queryResult)





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
def setup():
    pass

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
            # TODO: set to actual table containing device info, rather than the test table
            curs.execute("SELECT * FROM test")

            # commit cursor executions and return fetch results
            conn.commit()
            fetchResults = json.loads(json.dumps(curs.fetchall()))
            # print(fetchResults)
            return fetchResults
        
    except Error as e:
        print("[CONSOLE] ERROR: ", e)

# DEBUG: create some fake table and do stuff w/ it in SQL (technically sqlite3)
def testDB(cursor):

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

"""========== SCOPE =========="""

if __name__ == '__main__':
    main()

"""========== \/ @file END \/ =========="""
