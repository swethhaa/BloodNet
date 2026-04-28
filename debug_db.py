import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    cur.execute("SELECT requestid, bloodgroupreq, units, status FROM bloodrequest")
    requests = cur.fetchall()
    print("Requests:", requests)
    
    cur.execute("SELECT bloodgroup, unitsavailable FROM bloodstock")
    stock = cur.fetchall()
    print("Stock:", stock)
    
    conn.close()
except Exception as e:
    print("Error:", e)
