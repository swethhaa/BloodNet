import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    cur.execute("DESC donor")
    result = cur.fetchall()
    print("Donor table columns:")
    for col in result:
        print(f"  {col}")
    
    # Test SELECT *
    cur.execute("SELECT * FROM donor LIMIT 1")
    donor = cur.fetchone()
    print(f"\nSample donor record has {len(donor)} fields:")
    for i, val in enumerate(donor):
        print(f"  [{i}]: {val}")
    
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
