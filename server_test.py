import requests

url = "http://192.168.1.16:5000"

data = {
    "name": "Котик",
    "region": "Ленинградская область"
}

files = {
    "image": open("cats/0.jpg", "rb")
}

search = '/search'
add_cat = '/add_cat'

response = requests.post(url + search, data=data, files=files)
print(response.status_code)

response = requests.post(url + add_cat, data=data, files=files)
print(response.status_code)
