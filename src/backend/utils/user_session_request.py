import os
import json
import requests

client = requests.session()
login_url = "http://127.0.0.1:8000/users/login/"
logout_url = "http://127.0.0.1:8000/users/logout/"
login_data: dict[str, str] = {"username": "test1", "password": "Password1"}

print()
response: requests.Response = client.post(login_url, json=login_data)
print(response.status_code, response.json()["detail"])
print()
print(client.cookies)

# Save the session cookie
cookies = response.cookies
session_cookie = response.cookies['session']
headers = {
			'COOKIE': f'session={session_cookie}',
			'AUTHORIZATION': f'Token {session_cookie}'
		}

print()
response: requests.Response = client.delete(logout_url, cookies=cookies)
print(response.status_code, response.json()["detail"])

print()
response: requests.Response = client.delete(logout_url, headers=headers, cookies=cookies)
print(response.status_code, response.json()["detail"])