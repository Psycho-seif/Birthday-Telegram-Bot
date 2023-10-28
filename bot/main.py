import requests

# Requirements
USERNAME = "PythonAnywhere_Username"
SECRET = "long_auto-generated_key_to_avoid_external_interference"
AUTH_KEY = "Telegram_Bot_Auth_Key_(TOKEN)"
url = "https://" + USERNAME + ".pythonanywhere.com/" + SECRET

r = requests.post("{}/daily-reminder".format(url))
print("{} || {}".format(r.status_code, r.text))
