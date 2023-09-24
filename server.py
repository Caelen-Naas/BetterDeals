import flask
import requests
import glob
import json
from bs4 import BeautifulSoup
import os
import shutil
import argparse


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
logo_path: str = settings.get('logo_path').replace('(SUB)', subdirectory)

app = flask.Flask(__name__)


def parse_command_line() -> argparse.Namespace:
    """
    Parse the command line arguments using argparse
    :return: the parsed command line arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='debugger mode', action="store_true")

    return parser.parse_args()


def scrape_id(id: str) -> dict:
    """
    Scrape the data from the given id
    :param id: the id of the data
    :return: the data
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

    return data


def scrape_prices(product_name: str) -> dict:
    link = 'https://www.google.com/search?hl=en&tbm=shop&psb=1&q=' + product_name.replace(' ', '+')

    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    with open('test.txt', 'w') as file:
        file.write(str(soup))
    spans = soup.find_all('a')
    for span in spans:
        if span.has_attr('href'):
            print(span.text)



# Define a route and a function to handle the route
@app.route('/')
def serve_index():
    return flask.send_file(f'.{subdirectory}data{subdirectory}pub_site{subdirectory}index.html')


@app.route('/lookup', methods=['POST'])
def handle_lookup():
    upc = json.loads(flask.request.data.decode('utf-8'))['upc']  # Get the UPC code from the form
    
    ids = glob.glob(f'{dictionary_path}*.json')
    if f'{dictionary_path}{upc}.json' in ids:
        print('GLOB')
        return flask.jsonify(json.load(open(f'{dictionary_path}{upc}.json')))
    
    print('SCRAPE')
    data = scrape_id(upc)  # Scrape data for the provided UPC code
    return flask.jsonify(data)  # Return the scraped data as JSON


def print_logo():
    with open(logo_path, mode='r', encoding='utf-8') as file:
        print(file.read())


# Run the Flask app
if __name__ == '__main__':
    print_logo()
    args = parse_command_line()

    scrape_prices('12 Pack Mug Root Beer Fridge Pack')
    
    app.run(debug=args.debug, port=port)
