# Created by Patrick Archer on 15 April 2019

"""
@file is the main script that the Central Hub will operate from.
"""

"""========== IMPORTS =========="""

import sys
import json
import sqlite3
from sqlite3 import Error

"""========== GLOBAL VARS =========="""

# path to location database file
pathToDB = "database/locations.db"

"""========== MAIN() =========="""

def main():

    # try connecting to database file and attaching a cursor
    try:
        with sqlite3.connect(pathToDB) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()

            """DEBUG: test json parsing functionality"""
            results = testDB(cur)
            conn.commit()
            # convert returned data into a JSON dictionary
            y = json.loads(json.dumps(results))

            # print(results)
            # print(json.dumps(results))

            print(y)
            # print(y[0])
            # print(y[0]["num1"])

            # parse returned data; if value stored in num1 == 78.38, return corresponding str1 value
            for i in y:
                print(i, i["num1"], " ", i["num2"], " ", i["str1"])
                if i["num1"] == 78.38:
                    print(i["str1"])

            """DEBUG"""

    except Error as e:
        print("[CONSOLE] Error: ", e)

"""========== ADDITIONAL FUNCTIONS =========="""

# debug
def testDB(cursor):

    cursor.execute("DROP TABLE IF EXISTS test")

    cursor.execute("CREATE TABLE test"
                   "(num1 VALUE, num2 INTEGER, str1 TEXT)")

    cursor.execute("INSERT INTO test (num1, num2, str1)"
                   "VALUES (25.2, 10, 'row1')")

    cursor.execute("INSERT INTO test (num1, num2, str1)"
                   "VALUES (78.38, 55, 'row2')")

    cursor.execute("SELECT * FROM test")
    # cursor.execute("SELECT * FROM test WHERE str1=='row2'")

    fetch = cursor.fetchall()

    return fetch


# used to generate JSON-formatted data from database queries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


"""========== SCOPE =========="""

if __name__ == '__main__':
    main()

"""========== \/ END OF FILE \/ =========="""
