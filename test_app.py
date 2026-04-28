import sys
sys.path.insert(0, '/Users/sweth/Desktop/bloodbankproject')

try:
    from app import app
    print("App imported successfully")
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
