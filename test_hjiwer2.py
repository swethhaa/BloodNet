from app import app
import traceback

# Test with hjiwer donor
print("Testing donation for hjiwer (donorid=15)...")

try:
    with app.test_client() as client:
        # Login as admin
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        print(f"Login: {response.status_code}")
        
        # Try donation for hjiwer
        response = client.post('/donate', data={
            'donorid': '15',
            'bloodgroup': 'A+',
            'units': '1'
        }, follow_redirects=True)
        
        print(f"Donate: {response.status_code}")
        if response.status_code == 500:
            print("ERROR in response")
            # Print first 1000 chars
            print(response.data.decode()[:1000])
        else:
            print("SUCCESS!")
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
