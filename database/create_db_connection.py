import sqlite3

DATABASE = "database/ActsData.db"

def get_connection():
    
    return sqlite3.connect(DATABASE)