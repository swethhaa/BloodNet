import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    cur.execute("DESCRIBE hospital")
    print(cur.fetchall())
except Exception as e:
    print(e)
