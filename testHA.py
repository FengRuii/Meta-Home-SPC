import requests

# Replace with your Home Assistant instance URL and your access token
HOME_ASSISTANT_URL = 'http://homeassistant.local:8123/'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOTU1ZjA0ZTllYmY0NzkxYTdjNjdkMWViMWVhN2QwOSIsImlhdCI6MTcyMjc2Mzk1OSwiZXhwIjoyMDM4MTIzOTU5fQ.wGWQJYfsSdjxdsmU5hLL5t68xsaP0MuQtaB-MFL3A-s'

# Define your Home Assistant details
url_wiz = "http://homeassistant.local:8123/api/services/light/turn_on"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOTU1ZjA0ZTllYmY0NzkxYTdjNjdkMWViMWVhN2QwOSIsImlhdCI6MTcyMjc2Mzk1OSwiZXhwIjoyMDM4MTIzOTU5fQ.wGWQJYfsSdjxdsmU5hLL5t68xsaP0MuQtaB-MFL3A-s"
entity_id_wiz = "light.wiz_rgbw_tunable_4b588c"

url_honey = "http://homeassistant.local:8123/api/services/climate/set_temperature"
entity_id_honey = "climate.thermostat"


# Set the headers and payload
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data_wiz = {
    "entity_id": entity_id_wiz,
    "effect": "Romance"  # Replace with your desired RGB color values
}

data_honey ={
    "entity_id": entity_id_honey,
    "temperature": 78.0  # Replace with your desired temperature in Celsius
}

# Make the POST request to Home Assistant
response_wiz = requests.post(url_wiz, headers=headers, json=data_wiz)
response_honey = requests.post(url_honey, headers=headers, json=data_honey)


# Check the response
if response_wiz.status_code == 200:
    print("Success: The light color has been changed.")
else:
    print(f"Failed: {response.status_code} - {response.text}")

if response_honey.status_code == 200:
    print("Success: The temperature has been set.")
else:
    print(f"Failed: {response_honey.status_code} - {response_honey.text}")
