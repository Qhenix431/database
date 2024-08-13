import sqlite3

# Connect to the database
con = sqlite3.connect("database.db")
cur = con.cursor()

# Add a new boolean column to the sampleData table
cur.execute('INSERT INTO URL_MASTER (URL_NAME, URL, TYPE) VALUES (?,?,?)', ('abc', 'def', 'ghi'))

# Commit the changes and close the connection
con.commit()
con.close()
