import requests, json, re
from parsel import Selector

# https://docs.python-requests.org/en/master/user/quickstart/#passing-parameters-in-urls
params = {
    "q": "12 Pack Mug Root Beer Fridge Pack",
    "hl": "en",     # language
    "gl": "us",     # country of the search, US -> USA
    "tbm": "shop"   # google search shopping tab
}

# https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
selector = Selector(html.text)

def get_original_images():
    all_script_tags = "".join(
        [
            script.replace("</script>", "</script>\n")
            for script in selector.css("script").getall()
        ]
    )
    
    image_urls = []
    
    for result in selector.css(".Qlx7of .sh-dgr__grid-result"):
        # https://regex101.com/r/udjFUq/1
        url_with_unicode = re.findall(rf"var\s?_u='(.*?)';var\s?_i='{result.attrib['data-pck']}';", all_script_tags)

        if url_with_unicode:
            url_decode = bytes(url_with_unicode[0], 'ascii').decode('unicode-escape')
            image_urls.append(url_decode)
            
    return image_urls

def get_suggested_search_data():
    google_shopping_data = []

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
        # https://regex101.com/r/kAr8I5/1
        store_rating = re.search(r"^\S+", store_rating_value).group() if store_rating_value else store_rating_value

        store_reviews_value = result.css(".zLPF4b .XEeQ2 .ugFiYb::text").get()
        # https://regex101.com/r/axCQAX/1
        store_reviews = re.search(r"^\(?(\S+)", store_reviews_value).group() if store_reviews_value else store_reviews_value

        store_reviews_link_value = result.css(".zLPF4b .XEeQ2 .QhE5Fb::attr(href)").get()
        store_reviews_link = "https://www.google.com" + store_reviews_link_value if store_reviews_link_value else store_reviews_link_value

        compare_prices_link_value = result.css(".Ldx8hd .iXEZD::attr(href)").get()      
        compare_prices_link = "https://www.google.com" + compare_prices_link_value if compare_prices_link_value else compare_prices_link_value

        google_shopping_data.append({
            "title": title,
            "product_link": product_link,
            "product_rating": product_rating,
            "product_reviews": product_reviews,
            "price": price,
            "store": store,
            "thumbnail": thumbnail,
            "store_link": store_link,
            "delivery": delivery,
            "store_rating": store_rating,
            "store_reviews": store_reviews,
            "store_reviews_link": store_reviews_link,
            "compare_prices_link": compare_prices_link,
        })

    print(json.dumps(google_shopping_data, indent=2, ensure_ascii=False))

get_suggested_search_data()