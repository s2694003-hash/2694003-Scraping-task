import requests
from bs4 import BeautifulSoup

from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse
import time

# アクセスしたいWebサイトのURL
url = "https://www.musashino-u.ac.jp/"
domain = "www.musashino-u.ac.jp"                      # 同一ドメインの判定に使う
skip_ext = (".pdf", ".jpg", ".png", ".gif", ".zip")   # 非HTMLの拡張子

# サイトマップを格納する辞書（key: URL, value: <title>で挟まれた文字列）
sitemap = {}

# 訪問する予定のURLのキューと、訪問済みURLの集合
queue = deque([url])
seen = {url}

# 1. 同一ドメインの全ページを巡回する
while queue:
    page_url = queue.popleft()

    # Webサーバーにリクエストを出す
    try:
        res = requests.get(page_url, timeout=10)
        res.raise_for_status()
        res.encoding = 'utf-8'  # 文字コードをUTF-8に変換する
    except requests.RequestException as e:
        print(f"取得失敗:{page_url} ({e})")
        continue
    finally:
        time.sleep(1)  # サーバーへの負荷軽減のため1秒間スリープする

    # 2. <title>タグの文字列を辞書に格納する
    html_soup = BeautifulSoup(res.text, 'html.parser')
    sitemap[page_url] = html_soup.title.get_text(strip=True) if html_soup.title else ""
    print(f"{len(sitemap)}件目:{page_url}")

    # 3. ページ内のリンクをすべて集めてキューに追加する
    a_all = html_soup.find_all('a', href=True)
    for a in a_all:
        link = urldefrag(urljoin(page_url, a['href']))[0]  # 絶対URLに変換→#以下を除去
        parsed = urlparse(link)

        # 同一ドメインのHTMLページだけを訪問予定に入れる
        if parsed.netloc == domain and not link.lower().endswith(skip_ext) and link not in seen:
            seen.add(link)
            queue.append(link)

# サイトマップを表示する
for key, value in sitemap.items():
        print(f"{key}: {value}")

# with open("musashino-u.html", "w") as f:
#     f.write(res.text)



# 任意の属性で検索
tag_href_list = html_soup.find_all(attrs={"href": True})

for tag in tag_href_list:
    print(tag)