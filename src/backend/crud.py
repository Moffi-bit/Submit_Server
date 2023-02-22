import requests

data_json = {
    "email": "yessir@gmail",
    "user": "geek",
    "pass": "coding",
}

x = requests.post('http://127.0.0.1:5000/login/user/', data=data_json)

print(x.text)