import flask
import requests
import glob
import json
from bs4 import BeautifulSoup
import os
import shutil
import argparse
import scraper
import datetime


if os.name == 'nt':
    subdirectory = '\\'
else:
    subdirectory = '/'


if not os.path.exists(f'.{subdirectory}data{subdirectory}settings.json'):
    shutil.copyfile(f'.{subdirectory}data{subdirectory}backup{subdirectory}settings.json', f'.{subdirectory}data{subdirectory}settings.json')

settings: dict = json.load(open(f'.{subdirectory}data{subdirectory}settings.json'))

url: str = settings.get('scrape_url')
port: int = settings.get('port', 8080)
dictionary_path: str = settings.get('dictionary_path').replace('(SUB)', subdirectory)
price_dictionary_path: str = settings.get('price_dictionary_path').replace('(SUB)', subdirectory)
price_refresh_interval: int = settings.get('price_refresh_interval', 1) #days
date_format: str = settings.get('date_format', '%Y-%m-%d %H:%M:%S.%f')
logo_path: str = settings.get('logo_path').replace('(SUB)', subdirectory)
accepted_vendors: list = settings.get('accepted_vendors')

app = flask.Flask(__name__)


def parse_command_line() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='debugger mode', action="store_true")
    parser.add_argument('-p', '--port', help='port to run the server on', type=int)
    parser.add_argument('-fr', '--force_refresh', help='force refresh the data', action="store_true")


    return parser.parse_args()


def scrape_id(id: str) -> None:
    """
    Scrape data for the given ID and save it to a JSON file.
    :param id: The ID to scrape.
    """
    global url

    page = requests.get(url.replace('(BARCODE)', id))
    soup = BeautifulSoup(page.content, 'html.parser')
    trs = soup.find_all('tr')

    data = {'Description' : None, 'Size/Weight' : None,'Issuing Country' : None, 'Last Modified' : None}

    for tr in trs:
        for key in data.keys():
            if key in tr.text:
                data[key] = str(tr.text).replace(key, '').strip().replace('By\n\n', 'By: ')
    
    with open(f'{dictionary_path}{id}.json', 'w') as file:
        json.dump(data, file)


def scrape_prices(id, description, max_results=5, accepted_vendors=None) -> None:
    """
    Scrape price data for a product ID and save it to a JSON file.
    :param id: The product ID.
    :param description: The product description.
    :param max_results: Maximum number of results to scrape.
    :param accepted_vendors: List of accepted vendors.
    """
    global price_dictionary_path

    expiration = datetime.datetime.now() + datetime.timedelta(days=price_refresh_interval)
    
    data = scraper.scrape_google_shopping(description, max_results, accepted_vendors)
    with open(f'{price_dictionary_path}{id}.json', 'w') as file:
        json.dump({'expires': expiration.strftime(date_format), 'results' : data}, file)


# Define a route and a function to handle the route
@app.route('/')
def serve_index():
    """
    Serve the index HTML file.
    """

    return flask.send_file(f'.{subdirectory}data{subdirectory}pub_site{subdirectory}index.html')


@app.route('/lookup', methods=['POST'])
def handle_lookup():
    """
    Handle POST requests to perform lookup and return scraped data as JSON.
    """

    upc = json.loads(flask.request.data.decode('utf-8'))['upc']  # Get the UPC code from the form

    try:
        int(upc)
    except:
        return flask.jsonify({'error': 'Invalid UPC'})
    
    ids = glob.glob(f'{dictionary_path}*.json')
    prices = glob.glob(f'{price_dictionary_path}*.json')

    
    if f'{dictionary_path}{upc}.json' not in ids:
        print('GLOB')
        scrape_id(upc)
    
    data = json.load(open(f'{dictionary_path}{upc}.json'))
    
    if f'{price_dictionary_path}{upc}.json' not in prices:
        print('GLOB')
        scrape_prices(upc, data['Description'], accepted_vendors=accepted_vendors)
    
    price_data = json.load(open(f'{price_dictionary_path}{upc}.json'))

    if datetime.datetime.strptime(price_data['expires'], date_format) < datetime.datetime.now():
        print('SCRAPE')
        scrape_prices(upc, data['Description'], accepted_vendors=accepted_vendors)
        price_data = json.load(open(f'{price_dictionary_path}{upc}.json'))
    
    
    return flask.jsonify(data, price_data)  # Return the scraped data as JSON


def print_logo():
    """
    Print the contents of the logo file.
    """
    
    with open(logo_path, mode='r', encoding='utf-8') as file:
        print(file.read())


# Run the Flask app
if __name__ == '__main__':
    print_logo()
    args = parse_command_line()

    if args.port:
        port = args.port
    
    if args.force_refresh:
        ids = glob.glob(f'{dictionary_path}*.json')
        prices = glob.glob(f'{price_dictionary_path}*.json')

        for id in ids:
            os.remove(id)
        
        for price in prices:
            os.remove(price)
    
    app.run(debug=args.debug, port=port)
