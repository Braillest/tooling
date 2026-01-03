from bs4 import BeautifulSoup
import os
import requests

book_dir = "/data/books/"
text_dir = "/data/texts/"
url = "https://www.gutenberg.org/browse/scores/top"

print("Downloading top scoring books...")
response = requests.get(url)
response.raise_for_status()

print("Parsing HTML...")
html = response.content
soup = BeautifulSoup(html, "html.parser")
h2 = soup.find("h2", id="books-last1")
ol = h2.find_next_sibling("ol")

print("Extracting titles and links...")
reference_data = []
for li in ol.find_all("li"):

    # Strip trailing score from title and define book and text paths
    # Ex: title (text) here (123).txt -> title (text) here.txt
    title = "(".join(li.get_text().split("(")[:-1]).rstrip() + ".txt"

    reference_data.append({
        "title": title,
        "link": "https://www.gutenberg.org" + li.find("a")["href"] + ".txt.utf-8"
    })

print("Downloading books...")
process_data = []
for item in reference_data:

    # Check if book already exists
    if os.path.exists(book_dir + item["title"]):
        print("Skipping " + item["title"])
        continue

    # Check if text already exists
    if os.path.exists(text_dir + item["title"]):
        print("Skipping " + item["title"])
        continue

    print("Downloading " + item["title"])

    try:
        response = requests.get(item["link"])
        response.raise_for_status()
        process_data.append({
            "title": item["title"],
            "book": response.text
        })
    except:
        print("Failed to download " + item["title"])

# Free reference_data
reference_data = None
del reference_data

print("Processing books...")
for item in process_data:

    print("Processing " + item["title"])
    book_path = book_dir + item["title"]
    text_path = text_dir + item["title"]

    # Save complete context of the book for reference
    with open(book_path, "w", encoding="utf-8") as book_file:
        book_file.write(item["book"])

    # Skip gutenberg copyright and extract book text
    try:
        text = str(item["book"]).split("***")[2]
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)
    except:
        print("Failed to process " + item["title"])

# Free process_data
process_data = None
del process_data

print("Done!")
