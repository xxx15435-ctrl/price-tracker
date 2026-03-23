import requests
from bs4 import BeautifulSoup
import json
import os

# 🔍 搜尋網址（BigGo 最新排序）
URL = "https://biggo.com.tw/s/iPhone+17+Pro+Max+512GB/?sort=new"

# LINE Notify Token（從環境變數拿）
LINE_TOKEN = os.getenv("LINE_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def send_line(msg):
    requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {LINE_TOKEN}"},
        data={"message": msg}
    )

def load_seen():
    if os.path.exists("seen.json"):
        with open("seen.json", "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open("seen.json", "w") as f:
        json.dump(list(seen), f)

def main():
    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    items = soup.select("a")  # BigGo用a標籤抓連結（簡化版）

    seen = load_seen()
    new_seen = set(seen)

    count = 0

    for item in items:
        title = item.get_text(strip=True)
        link = item.get("href")

        if not link or "http" not in link:
            continue

        # 只抓包含關鍵字的
        if "iPhone" not in title:
            continue

        if link not in seen:
            msg = f"🆕 新商品！\n{title}\n{link}"
            send_line(msg)
            new_seen.add(link)
            count += 1

        if count >= 5:
            break

    save_seen(new_seen)

if __name__ == "__main__":
    main()
