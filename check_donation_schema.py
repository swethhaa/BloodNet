import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    print("donation table columns:")
    cur.execute("DESC donation")
    result = cur.fetchall()
    for col in result:
        print(f"  {col[0]}: {col[1]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
