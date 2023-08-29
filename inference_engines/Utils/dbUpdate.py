import sqlite3
import pandas as pd

dbcon = sqlite3.connect('cdss.db')


df = pd.read_sql_query("SELECT * FROM PRESCRIPTION WHERE SCHEDULE = 'SN' AND FIXEDTIME = 'F' " , dbcon)
print(df.to_markdown())

dbcon.execute("UPDATE PRESCRIPTION SET FIXEDTIME = 'N' WHERE SCHEDULE = 'SN'")

dbcon.commit()
dbcon.close()