import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    # Show all tables
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print("Tables in bloodbank database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check bloodexpiry
    print("\nLooking for expiry/blood stock related tables...")
    for table in tables:
        table_name = table[0]
        if 'blood' in table_name.lower() or 'expir' in table_name.lower() or 'stock' in table_name.lower():
            print(f"\n{table_name} columns:")
            cur.execute(f"DESC {table_name}")
            cols = cur.fetchall()
            for col in cols:
                print(f"    {col[0]}: {col[1]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
