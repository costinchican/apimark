import requests
import json

user1={ "firstname": "Dorin",
        "lastname": "Calinescu",
        "age": 60,
        "city": "Bucharest"
    }

BASE= "http://127.0.0.1:5000/"
response = requests.post(BASE + "user/1149", user1)
print(response.json())