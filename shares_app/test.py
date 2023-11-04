import http.client
import requests

conn = http.client.HTTPSConnection("send.api.mailtrap.io")

payload = "{\n  \"to\": [\n    {\n      \"email\": \"john_doe@example.com\",\n      \"name\": \"John Doe\"\n    }\n  ],\n  \"cc\": [\n    {\n      \"email\": \"jane_doe@example.com\",\n      \"name\": \"Jane Doe\"\n    }\n  ],\n  \"bcc\": [\n    {\n      \"email\": \"james_doe@example.com\",\n      \"name\": \"Jim Doe\"\n    }\n  ],\n  \"from\": {\n    \"email\": \"sales@example.com\",\n    \"name\": \"Example Sales Team\"\n  },\n  \"attachments\": [\n    {\n      \"content\": \"PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KCiAgICA8aGVhZD4KICAgICAgICA8bWV0YSBjaGFyc2V0PSJVVEYtOCI+CiAgICAgICAgPG1ldGEgaHR0cC1lcXVpdj0iWC1VQS1Db21wYXRpYmxlIiBjb250ZW50PSJJRT1lZGdlIj4KICAgICAgICA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEuMCI+CiAgICAgICAgPHRpdGxlPkRvY3VtZW50PC90aXRsZT4KICAgIDwvaGVhZD4KCiAgICA8Ym9keT4KCiAgICA8L2JvZHk+Cgo8L2h0bWw+Cg==\",\n      \"filename\": \"index.html\",\n      \"type\": \"text/html\",\n      \"disposition\": \"attachment\"\n    }\n  ],\n  \"custom_variables\": {\n    \"user_id\": \"45982\",\n    \"batch_id\": \"PSJ-12\"\n  },\n  \"headers\": {\n    \"X-Message-Source\": \"dev.mydomain.com\"\n  },\n  \"subject\": \"Your Example Order Confirmation\",\n  \"text\": \"Congratulations on your order no. 1234\",\n  \"category\": \"API Test\"\n}"

headers = {
    'Content-Type': "application/json",
    'Accept': "application/json",
    'Api-Token': "Bearer 5bcb506fa84e7ae2c49a984d8ae05907"
}

conn.request("POST", "/api/send", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

response = requests.request(method="POST", url="https://send.api.mailtrap.io/api/send", headers=headers, params=payload)

print(response.json())
