from app import app, mysql, build_donors_with_status
from flask import request
from datetime import date

# Test the build_donors_with_status function
print("Testing build_donors_with_status function...")

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM donor LIMIT 1")
        donor_sample = cur.fetchone()
        print(f"Sample donor: {donor_sample}")
        
        cur.execute("SELECT * FROM donor")
        donors = cur.fetchall()
        print(f"Total donors: {len(donors)}")
        
        donors_with_status = build_donors_with_status(donors)
        print(f"Built status list: {len(donors_with_status)} items")
        print("First donor with status:")
        print(f"  Donor: {donors_with_status[0][0]}")
        print(f"  Status: {donors_with_status[0][1]}")
        print(f"  Eligible: {donors_with_status[0][2]}")
        
        cur.close()
        print("\n✓ Function works correctly!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
