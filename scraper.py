import requests
import re
from parsel import Selector
from urllib.parse import urlparse, parse_qs


def extract_actual_vendor_link(google_redirect_url: str) -> str:
    """
    Extract the actual vendor link from a Google redirect URL.

    :param google_redirect_url: The Google redirect URL.
    :return: The actual vendor link.
    """
    
    parsed_url = urlparse(google_redirect_url)

    query_parameters = parse_qs(parsed_url.query)
    actual_vendor_link = query_parameters.get('url', [None])[0]

    return actual_vendor_link


def scrape_google_shopping(query: str, max_results: int = 10, accepted_vendors: list = None) -> list:
    """
    Scrape product data from Google Shopping based on a query.

    :param query: The search query.
    :param max_results: Maximum number of results to scrape.
    :param accepted_vendors: List of accepted vendors to filter results.
    :return: A list of dictionaries containing product data.
    """

    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "tbm": "shop"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }

    # Send a request to Google
    try:
        response = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return

    # Create a Selector object
    selector = Selector(response.text)

    def get_original_images() -> list:
        """
        Extract original image URLs from Google Shopping results.

        :return: A list of original image URLs.
        """
        
        all_script_tags = "".join(
            [
                script.replace("</script>", "</script>\n")
                for script in selector.css("script").getall()
            ]
        )

        image_urls = []

        for result in selector.css(".Qlx7of .sh-dgr__grid-result"):
            url_with_unicode = re.findall(rf"var\s?_u='(.*?)';var\s?_i='{result.attrib['data-pck']}';", all_script_tags)

            if url_with_unicode:
                url_decode = bytes(url_with_unicode[0], 'ascii').decode('unicode-escape')
                image_urls.append(url_decode)

        return image_urls

    def get_suggested_search_data() -> list:
        """
        Extract product data from Google Shopping results.

        :return: A list of dictionaries containing product data.
        """
        google_shopping_data = []
        result_count = 1

        for result, thumbnail in zip(selector.css(".Qlx7of .i0X6df"), get_original_images()):

            title = result.css(".tAxDx::text").get()
            product_link = "https://www.google.com" + result.css(".Lq5OHe::attr(href)").get()
            product_rating = result.css(".NzUzee .Rsc7Yb::text").get()
            product_reviews = result.css(".NzUzee > div::text").get()
            price = result.css(".a8Pemb::text").get()
            store = result.css(".aULzUe::text").get()
            store_link = "https://www.google.com" + result.css(".eaGTj div a::attr(href)").get()
            delivery = result.css(".vEjMR::text").get()

            store_rating_value = result.css(".zLPF4b .XEeQ2 .QIrs8::text").get()
            store_rating = re.search(r"^\S+", store_rating_value).group() if store_rating_value else store_rating_value

            store_reviews_value = result.css(".zLPF4b .XEeQ2 .ugFiYb::text").get()
            store_reviews = re.search(r"^\(?(\S+)", store_reviews_value).group() if store_reviews_value else store_reviews_value

            store_reviews_link_value = result.css(".zLPF4b .XEeQ2 .QhE5Fb::attr(href)").get()
            store_reviews_link = "https://www.google.com" + store_reviews_link_value if store_reviews_link_value else store_reviews_link_value

            compare_prices_link_value = result.css(".Ldx8hd .iXEZD::attr(href)").get()
            compare_prices_link = "https://www.google.com" + compare_prices_link_value if compare_prices_link_value else compare_prices_link_value
            
            white_listed = False

            for vendor in accepted_vendors:
                if vendor.lower() in store.lower():
                    white_listed = True
                    break
            
            if not white_listed:
                continue

            google_shopping_data.append({
                "title": title,
#                "product_link": product_link,
#                "product_rating": product_rating,
#                "product_reviews": product_reviews,
                "price": price,
                "store": store,
#                "thumbnail": thumbnail,
                "store_link": extract_actual_vendor_link(store_link),
                "delivery": delivery,
#                "store_rating": store_rating,
#                "store_reviews": store_reviews,
#                "store_reviews_link": store_reviews_link,
#                "compare_prices_link": compare_prices_link,
            })

            result_count += 1

            if result_count > max_results:
                break

        return google_shopping_data

    return get_suggested_search_data()