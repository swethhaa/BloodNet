import MySQLdb
try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    # Check if columns exist
    cur.execute("SHOW COLUMNS FROM hospital LIKE 'username'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE hospital ADD COLUMN username VARCHAR(50) UNIQUE")
        print("Added username column.")
        
    cur.execute("SHOW COLUMNS FROM hospital LIKE 'password'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE hospital ADD COLUMN password VARCHAR(100)")
        print("Added password column.")
        
    # Update existing rows with dummy usernames so we don't have NULLs
    cur.execute("SELECT hospitalid, hospitalname FROM hospital WHERE username IS NULL")
    rows = cur.fetchall()
    for row in rows:
        hid = row[0]
        hname = row[1]
        dummy_user = f"hosp{hid}_{hname.replace(' ', '').lower()}"[:50]
        cur.execute("UPDATE hospital SET username=%s, password='password123' WHERE hospitalid=%s", (dummy_user, hid))
    print("Updated existing hospitals with dummy credentials.")
    
    conn.commit()
    conn.close()
    print("Database schema update complete.")
except Exception as e:
    print("Error:", e)
