import requests
response = requests.get('https://haha-phi-lilac.vercel.app/login')
html_response = response.text
for line in html_response.splitlines():
    if 'action=' in line or '<form' in line:
        print(line)
