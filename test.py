import requests

# Define the URL of your Express.js server's POST endpoint
url = 'http://localhost:3000/post'  # Update the URL as needed

# Data to send in the POST request
data = {'key1': 'value1', 'key2': 'value2'}

# Send the POST request
response = requests.post(url, json=data)

# Check the response from the server
if response.status_code == 200:
    # Request was successful
    print("Server Response:", response.text)
else:
    # Request failed
    print("Request failed with status code:", response.status_code)
