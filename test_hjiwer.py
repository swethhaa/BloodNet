from app import app

# Test with hjiwer donor
print("Testing donation for hjiwer (donorid=15)...")

with app.test_client() as client:
    with app.test_request_context():
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
        print(f"Response text:\n{response.data.decode()[:2000]}")
