import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    cur.execute("SHOW COLUMNS FROM bloodstock LIKE 'stockid'")
    if not cur.fetchone():
        cur.execute("""
            ALTER TABLE bloodstock 
            ADD COLUMN stockid INT AUTO_INCREMENT UNIQUE FIRST
        """)
        print("Added stockid column to bloodstock table.")
    else:
        print("stockid column already exists.")
    
    conn.commit()
    conn.close()
    print("Migration complete.")
except Exception as e:
    print("Error:", e)
