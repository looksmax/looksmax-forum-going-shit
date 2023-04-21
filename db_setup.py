
from time import sleep

input('Are you sure?')

sleep(15)

import os, header
try:
    os.remove(header.DB_FILE_NAME)
    print("Deleted existing database.")
except FileNotFoundError:
    pass

import sqlite3

conn = sqlite3.connect(header.DB_FILE_NAME)
print("Opened database successfully.")

with conn:

    conn.execute('''CREATE TABLE Members
            (ID INTEGER PRIMARY KEY NOT NULL,
             MEMBER_ID      INT     NOT NULL,
             NAME           TEXT    NOT NULL,
             JOIN_DATE      INT     NOT NULL,
             POSTS_COUNT    INT     NOT NULL,
             REP_SCORE      INT     NOT NULL,
             _REP_RATIO     REAL    GENERATED ALWAYS AS ( CAST(REP_SCORE AS REAL) / CAST(POSTS_COUNT AS REAL) ) VIRTUAL
            );''')
    print("Members table created successfully.")

    conn.execute('''CREATE TABLE Reacts
            (ID INTEGER PRIMARY KEY     NOT NULL,
             POST_ID        INT     NOT NULL,
             MEMBER_ID      INT     NOT NULL,
             REACT_DATE     INT     NOT NULL,
             REACT_TYPE     TEXT    NOT NULL
            );''')
    print("Reacts table created successfully.")

    conn.execute('''CREATE TABLE Posts
            (ID INTEGER PRIMARY KEY     NOT NULL,
             POST_ID        INT     NOT NULL,
             THREAD_ID      INT     NOT NULL,
             POST_DATE      INT     NOT NULL,
             MEMBER_ID      INT     NOT NULL,
             BODY_TEXT      TEXT    NOT NULL,
             IS_1ST_IN_THREAD  BOOL NOT NULL,
             REACTS_COUNT   INT     NOT NULL,
             _BODY_LENGTH   INT     GENERATED ALWAYS AS ( length(BODY_TEXT) ) STORED
            );''')
    print("Posts table created successfully.")

    conn.execute('''CREATE TABLE Threads
            (ID INTEGER PRIMARY KEY     NOT NULL,
             THREAD_ID      INT     NOT NULL,
             MEMBER_ID      INT     NOT NULL,
             POST_DATE      INT     NOT NULL,
             SUBFORUM       TEXT    NOT NULL,
             PREFIX         TEXT    NOT NULL,
             TITLE_TEXT     TEXT    NOT NULL,
             _TITLE_LENGTH  INT     GENERATED ALWAYS AS ( length(TITLE_TEXT) ) STORED
            );''')
    print("Threads table created successfully.")

print("Transaction completed successfully.")

conn.close()
