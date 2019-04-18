# Created by Patrick Archer on 15 April 2019

"""
@file is meant to be executed on the Central Hub, as that is where the location database will be stored.

More instructions can be found at:
    https://docs.python.org/2/library/sqlite3.html
"""

####################################

import sqlite3

####################################

def database():

    """
    INSTRUCTIONS:

    First,

    >>import sqlite3

    To connect to a database file, use the following cmd:

    >> conn = sqlite3.connect('example.db')

    Once you have a Connection, you can create a Cursor object and call its execute() method to perform SQL commands:

    >> c = conn.cursor()

    Example: Create table
    >> c.execute('''CREATE TABLE stocks
                 (date text, trans text, symbol text, qty real, price real)''')

    Example: Insert a row of data
    >> c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

    Example: Save (commit) the changes
    >> conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    >> conn.close()
    """

####################################