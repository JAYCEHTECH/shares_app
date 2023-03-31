import requests
# API URL
quicksend_url = "https://uellosend.com/quicksend/"
data = {
        'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
        'sender_id': 'UelloPy',
        'message': 'Hello testing python integration',
        'recipient': '0242442147'
        }


headers = {'Content-type': 'application/json'}


response = requests.post(quicksend_url, headers=headers, json=data)



print(response.json())
