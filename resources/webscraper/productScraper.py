import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

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


# Returns a specified amount of reviews in an array
def reviews(soup):
    data_str = ""
    className = "a-expander-content reviewText review-text-content a-expander-partial-collapse-content"

    # Collects a predefined number of reviews
    for i in range(1, maxReviews + 1):
        try:
            item = soup.find_all("div", class_=className)[i]
            if len(str(item.get_text())) > minSizeReview:
                data_str = data_str + str(item.get_text())
            else:
                print("review too short")
        except:
            print("review error")

    data_str = data_str.split("\n")
    while '' in data_str:
        data_str.remove('')

    return (str(data_str))


# Returns a URL to the landing image
def productImage(soup):
    source = "no image"
    # For a list of all images use the code described here:
    # https://proxyway.com/knowledge-base/how-to-get-src-attribute-from-img-tag-using-beautifulsoup
    # Search for all image tags and use the first one
    try:
        element = soup.find_all("img", class_="a-dynamic-image")[0]
    # Extract the 'src' attribute
        source = element['src']
    except:
        print("no image found")

    return (source)


################################
# ! Change Parameters here
filepath = 'ASIN.csv'
maxReviews = 5
minSizeReview = 20
################################


with open(filepath) as csv_file:
    csv_reader = csv.reader(csv_file)
    rows = list(csv_reader)

counter = 0

for row in rows:
    url = "https://www.amazon.com/-/de/dp/" + row[1]

    soup = html_code(url)

    data = {'category': row[0], 'image': productImage(soup), 'reviews': [
        reviews(soup)]}

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save the output.
    df.to_csv('amazon_data_V3.csv', mode='a', index=False, header=False)

    print(str(counter) + " " + row[0])
    counter = counter + 1
