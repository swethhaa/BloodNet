import MySQLdb

try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    # Check current null stockids
    print("Checking for null stockid values...")
    cur.execute("SELECT requestid, bloodgroupreq FROM bloodrequest WHERE stockid IS NULL")
    null_requests = cur.fetchall()
    print(f"Found {len(null_requests)} requests with null stockid")
    
    # Update null stockids by joining with bloodstock table
    if null_requests:
        print("\nUpdating stockid values...")
        cur.execute("""
            UPDATE bloodrequest br
            JOIN bloodstock bs ON br.bloodgroupreq = bs.bloodgroup
            SET br.stockid = bs.stockid
            WHERE br.stockid IS NULL
        """)
        conn.commit()
        print(f"Updated {cur.rowcount} records")
        
        # Verify the update
        cur.execute("SELECT requestid, bloodgroupreq, stockid FROM bloodrequest WHERE stockid IS NULL")
        remaining_nulls = cur.fetchall()
        if remaining_nulls:
            print(f"\nWarning: {len(remaining_nulls)} requests still have null stockid")
            for req in remaining_nulls:
                print(f"  Request {req[0]}: Blood Group {req[1]} - No matching stock found")
        else:
            print("Success! All stockid values have been populated.")
    else:
        print("No null stockid values found.")
    
    # Show final state
    cur.execute("SELECT COUNT(*) FROM bloodrequest WHERE stockid IS NOT NULL")
    populated = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bloodrequest")
    total = cur.fetchone()[0]
    print(f"\nFinal state: {populated}/{total} requests have stockid values")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print("Error:", e)
