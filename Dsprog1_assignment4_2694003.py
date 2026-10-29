import requests
from bs4 import BeautifulSoup
import time

# Define the URL of the website you want to scrape
url = "https://www.musashino-u.ac.jp/"
res = requests.get(url)
res.encoding = "utf-8"

# beautifulsoup
html_soup = BeautifulSoup(res.text,'html.parser')

with open("musashino-u.html", "w") as f:
    f.write(res.text)

# 任意の属性で検索
tag_href_list = html_soup.find_all(attrs={"href="})

for tag in tag_href_list:
    print(tag)