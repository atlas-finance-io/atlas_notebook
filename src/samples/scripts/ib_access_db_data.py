# -*- coding: utf-8 -*-
"""
IB API - accessing data in the sql db

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

import sqlite3

db = sqlite3.connect('D:/Udemy/Interactive Brokers Python API/10_streaming_ticks/ticks.db')
c=db.cursor()

#print out names of all the tables in DB
c.execute('SELECT name from sqlite_master where type= "table"')
c.fetchall()

#print out the columns and column types of a given table
c.execute('''PRAGMA table_info(TICKER0)''')
c.fetchall()

#print all rows for a given table
for m in c.execute('''SELECT * FROM TICKER0'''):
    print(m)
