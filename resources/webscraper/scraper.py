import requests
from bs4 import BeautifulSoup
import pandas as pd


# Define the header, so that the website doesn't block the access
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
			AppleWebKit/537.36 (KHTML, like Gecko) \
			Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


# Send the request
def getData(url):
    r = requests.get(url, headers=HEADERS)
    return r.text


# Convert data into HTML code and parse it
def html_code(url):

    # pass the url into getData function
    htmlData = getData(url)
    soup = BeautifulSoup(htmlData, 'html.parser')

    return (soup)


def getASIN(soup):
    className = "sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"
    data_str = []

    for item in soup.find_all("div", class_=className):
        data_str.append(item['data-asin'])

    return (data_str)


########################
# ! Change Search-Terms here
searchTerms = ["t-shirt", "shirt", "sweater", "shoes", "sandals", "jacket", "trousers", "shorts"]
########################

for index in range(0, len(searchTerms)):
    url_1 = "https://www.amazon.com/-/de/s?k="
    url_2 = "&page="

    numberOfPages = 5

    for page in range(1, numberOfPages + 1):
        url = url_1 + "mens+" + searchTerms[index] + url_2 + str(page)

        soup = html_code(url)

        data = {'Category': searchTerms[index], 'ASIN': getASIN(soup)}

        # Create DataFrame
        df = pd.DataFrame(data)

        # Save the output.
        df.to_csv('asin_V3.csv', mode='a', index=False, header=False)

        print(searchTerms[index] + " page " + str(page))

print("Finished collecting ASINs. Product scraping is starting now.")
import productScraper
