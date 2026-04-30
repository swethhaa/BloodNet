import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
cur = conn.cursor()

print("Testing query:")
cur.execute('SELECT stockid, bloodgroup, unitsavailable FROM bloodstock WHERE bloodgroup IS NOT NULL ORDER BY stockid')
data = cur.fetchall()

for row in data:
    print(f"Row: {row}, Type: {type(row)}")

cur.close()
conn.close()
