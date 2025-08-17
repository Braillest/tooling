import requests
from bs4 import BeautifulSoup

book_dir = "/data/books/"
text_dir = "/data/texts/"
url = "https://www.gutenberg.org/browse/scores/top"

response = requests.get(url)
response.raise_for_status()
html = response.content
soup = BeautifulSoup(html, "html.parser")
h2 = soup.find("h2", id="books-last1")
ol = h2.find_next_sibling("ol")
titles = [li.get_text() for li in ol.find_all("li")]
links = ["https://www.gutenberg.org" + a["href"] + ".txt.utf-8" for a in ol.find_all("a")]
books = [requests.get(link).text for link in links]

for title, book in zip(titles, books):

    # Save complete context of the book for reference
    with open(book_dir + title + ".txt", "w") as file:
        file.write(book)

    # Skip gutenberg copyright and extract book text
    try:
        text = str(book).split("***")[2]
        with open(text_dir + title + ".txt", "w") as file:
            file.write(text)
    except:
        print(title)
