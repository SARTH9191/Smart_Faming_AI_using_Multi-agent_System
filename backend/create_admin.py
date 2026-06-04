import urllib.request
import json

url = "http://localhost:8000/admin/register"
data = json.dumps({"username": "admin", "password": "adminpassword123", "super_secret": "agri_admin_secret_2026", "role": "superadmin"}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print(f"Error: {e}")
