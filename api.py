
import sqlite3
import pandas as pd

con = sqlite3.connect("database.db")

cur = con.cursor()
cur.execute(
    '''CREATE TABLE sampleData (
    PID TEXT,
    ORDER_ID TEXT,
    FIN TEXT,
    EN_LOC_NURSE_UNIT_DISP TEXT,
    ACCN TEXT,
    ORDER_MNEMONIC TEXT,
    TASK_ASSAY_CD TEXT,
    R_TASK_ASSAY_DISP TEXT,
    RESULT_VALUE_NUMERIC REAL,
    PERFORM_DT_TM TEXT
    )
    ''')

df = pd.read_csv('ResultsSampleData.csv')
df['PERFORM_DT_TM'] = pd.to_datetime(df['PERFORM_DT_TM'], format='%d/%m/%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')
df.to_sql('sampleData', con, if_exists='append', index=False)

# Commit the changes and close the connection
con.commit()
con.close()
