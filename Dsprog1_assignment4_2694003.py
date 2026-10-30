import requests
from bs4 import BeautifulSoup

from collections import deque
from urllib.parse import unquote, urljoin, urldefrag, urlparse
import time

import csv

# アクセスしたいWebサイトのURL
url = "https://www.musashino-u.ac.jp/"
domain = "www.musashino-u.ac.jp"                      # 同一ドメインの判定に使う
skip_ext = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".doc", ".docx",
            ".xls", ".xlsx", ".ppt", ".pptx", ".mp4", ".mp3", ".csv")  # 非HTMLの拡張子

# URLの表記ゆれ（http/https・/index.html・末尾スラッシュ）を1つにまとめる
def normalize(link):
    parsed = urlparse(link)
    path = parsed.path
    path = unquote(parsed.path)               # %E9%AB%98... → 高...（日本語表記にそろえる）
    if path.endswith("/index.html"):          # /guide/index.html → /guide/
        path = path[:-len("/index.html")]
    if "." not in path.rsplit("/", 1)[-1] and not path.endswith("/"):
        path += "/"                           # /guide → /guide/（.html等のファイルはそのまま）
    query = f"?{parsed.query}" if parsed.query else ""
    return f"https://{domain}{path}{query}"

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

        # 同一ドメインのページだけを訪問予定に入れる
        if parsed.netloc != domain:
            continue

        link = normalize(link)  # http/https・index.html・スラッシュの表記ゆれを統一

        # 非HTMLファイルを除外し、未訪問のURLだけをキューに追加する
        if not link.lower().endswith(skip_ext) and link not in seen:
            seen.add(link)
            queue.append(link)

# 4. 辞書の内容をCSVファイルに書き込む
with open("Dsprog1_assignment4_2694003.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Title"])
    for page_url, title in sitemap.items():
        writer.writerow([page_url, title])

# # サイトマップを表示する
# for key, value in sitemap.items():
#         print(f"{key}: {value}")

# with open("musashino-u.html", "w") as f:
#     f.write(res.text)

# # 任意の属性で検索
# tag_href_list = html_soup.find_all(attrs={"href": True})

# for tag in tag_href_list:
#     print(tag)

print(f"完了:{len(sitemap)}ページをCSVに保存しました")