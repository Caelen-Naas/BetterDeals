# BetterDeals
Takes a barcode as an input and scans the internet looking for the same product but at cheaper vendors 

## Server (`server.py`)
### Overview
The `server.py` script is a Python server that provides a web interface for looking up product information based on UPC (Universal Product Code) or barcode. It utilizes the Flask web framework and includes functions for scraping product details and prices from external sources.

### Usage
To run the server, execute server.py using a Python interpreter. You can optionally specify command-line arguments to customize its behavior.

#### <b><u>Command-Line Arguments</u></b>
- `-d` or `--debug`: Enable debugger mode.
- `-p` or `--port`: Specify the port to run the server on.
- `-fr` or `--force_refresh`: Force a data refresh by clearing cached data.

#### <b><u>Functions</u></b>
The server script includes several functions:

1. parse_command_line(): Parses command-line arguments and returns an argparse Namespace object.

2. scrape_id(id: str): Scrapes data for a given ID (barcode) and saves it to a JSON file.

3. scrape_prices(id, description, max_results=5, accepted_vendors=None): Scrapes price data for a product ID and saves it to a JSON file.

4. serve_index(): Serves the index HTML file for the web interface.

5. handle_lookup(): Handles POST requests to perform lookup and returns scraped data as JSON.

6. print_logo(): Prints the contents of a logo file.

#### <b><u>Configuration</u></b>

The server script uses a configuration file named `settings.json`` to customize its behavior. 

Info it uses:
- URL
- PORT
- FILE PATHS
- EXPIRATION DELAYS
- ACCEPTED VENDORS
- ETC

&nbsp;

## Scraper (`scraper.py`)

### Overview
The `scraper.py` script contains functions for scraping product data from Google Shopping based on a search query. It uses the requests library and parsel for web scraping.

### Functions
1. `extract_actual_vendor_link(google_redirect_url: str)`: Extracts the actual vendor link from a Google Shopping redirect URL.

2. `scrape_google_shopping(query: str, max_results: int = 10, accepted_vendors: list = None)`: Scrapes product data from Google Shopping based on a query.

### Usage
You can import and use the `scrape_google_shopping` function in your server script to retrieve product data.

&nbsp;

## HTML (`index.html`)

### Overview
The `index.html` file is an HTML template for the web interface of the product lookup system. It includes JavaScript code for barcode scanning using the QuaggaJS library, displaying results, and making requests to the server.

### Features
- Camera access for barcode scanning.
- Real-time scanning and display of product data.
- Search by entering a barcode ID.
- Display of product details, including titles, prices, and stores.

### Dependencies
The HTML file depends on the QuaggaJS library for barcode scanning. It also makes AJAX requests to the server for product lookup.

&nbsp;

## Getting Started
1. Make sure you have Python installed on your system.

2. Install the required Python packages using `pip install -r requirements.txt`

3. Configure the settings.json file with your desired settings.

4. Run the server script using python server.py.

5. Access the web interface by opening a web browser and navigating to the provided server URL.

6. Use the camera to scan barcodes or enter barcode IDs manually for product lookup.

7. View product details and prices retrieved from Google Shopping.