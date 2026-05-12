"import requests
password = "misuma123!"
url = "https://jamalnggau.pythonanywhere.com/login" + "/login"
data = {"password": password}
response = requests.post(url, data=data)
penerima = response.json()
penerima