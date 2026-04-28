from app import app
from datetime import date

# Test the donate POST endpoint
print("Testing donate POST endpoint...")

with app.test_client() as client:
    with app.test_request_context():
        # First, login as admin
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        print(f"Login response: {response.status_code}")
        
        # Now test the donate endpoint
        response = client.post('/donate', data={
            'donorid': '14',
            'bloodgroup': 'B+',
            'units': '1'
        }, follow_redirects=True)
        
        print(f"Donate response: {response.status_code}")
        print(f"Response URL: {response.request.path if response.request else 'N/A'}")
        
        if response.status_code != 200:
            print(f"Response text (first 500 chars):\n{response.data.decode()[:500]}")
            print("\nLooking for error message...")
            if b"Internal Server Error" in response.data:
                print("ERROR: Internal Server Error occurred")
            if b"Traceback" in response.data:
                print("Found traceback in response - likely a detailed error page")
