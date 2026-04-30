import MySQLdb

try:
    conn = MySQLdb.connect(host='127.0.0.1', user='root', password='Swe21tha07$', db='bloodbank')
    cur = conn.cursor()
    
    # Add phone column to donor table
    print("Checking donor table columns...")
    cur.execute("SHOW COLUMNS FROM donor LIKE 'phone'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE donor ADD COLUMN phone VARCHAR(13) DEFAULT NULL")
        print("✓ Added phone column to donor table")
    else:
        print("✓ Phone column already exists in donor table")
    
    # Add phone and address columns to hospital table
    print("\nChecking hospital table columns...")
    cur.execute("SHOW COLUMNS FROM hospital LIKE 'phone'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE hospital ADD COLUMN phone VARCHAR(13) DEFAULT NULL")
        print("✓ Added phone column to hospital table")
    else:
        print("✓ Phone column already exists in hospital table")
    
    cur.execute("SHOW COLUMNS FROM hospital LIKE 'address'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE hospital ADD COLUMN address VARCHAR(255) DEFAULT NULL")
        print("✓ Added address column to hospital table")
    else:
        print("✓ Address column already exists in hospital table")
    
    conn.commit()
    conn.close()
    print("\nDatabase schema update complete!")
    
except Exception as e:
    print(f"Error: {e}")
