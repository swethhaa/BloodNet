import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    bloodgroup = 'AB+'
    
    cur.execute("""
        SELECT requestid, units 
        FROM bloodrequest 
        WHERE bloodgroupreq=%s AND status='Not Available'
        ORDER BY requestid ASC
    """, (bloodgroup,))
    
    pending_requests = cur.fetchall()
    print("Pending requests for", bloodgroup, ":", pending_requests)
    
    for req in pending_requests:
        req_id = req[0]
        req_units = req[1]
        
        cur.execute("SELECT unitsavailable FROM bloodstock WHERE bloodgroup=%s", (bloodgroup,))
        stock_row = cur.fetchone()
        print(f"Checking request {req_id} (needs {req_units}). Current stock: {stock_row}")
        
        if stock_row and stock_row[0] >= req_units:
            print(f"Stock sufficient! Deducting {req_units} and updating status.")
            
            cur.execute("""
                UPDATE bloodstock 
                SET unitsavailable = unitsavailable - %s 
                WHERE bloodgroup=%s
            """, (req_units, bloodgroup))
            
            cur.execute("""
                UPDATE bloodrequest 
                SET status='Available' 
                WHERE requestid=%s
            """, (req_id,))
            
    conn.commit()
    conn.close()
    print("Done")
except Exception as e:
    print("Error:", e)
