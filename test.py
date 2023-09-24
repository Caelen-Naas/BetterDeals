import requests

# Define the URL of your Flask server
server_url = 'http://localhost:8080/lookup'  # Replace with your server's URL

# Define the UPC barcode you want to send in the POST request
barcode = '0028400090858'  # Replace with the desired barcode

# Create a dictionary with the data to be sent in the POST request
data = {'upc': barcode}

# Send the POST request to the server
response = requests.post(server_url, data=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse and print the JSON response from the server
    response_data = response.json()
    print("Scraped Data:")
    print(response_data)
else:
    print(f"Failed to fetch data. Status Code: {response.status_code}")
