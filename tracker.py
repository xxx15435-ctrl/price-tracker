import requests
from bs4 import BeautifulSoup
import json
import os

# 目標：iPhone 17 Pro Max 512GB (注意：2026年這應該是最新款，但網站架構可能會有反爬蟲)
URL = "https://biggo.com.tw/s/iPhone+17+Pro+Max+512GB/?sort=new"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_telegram(msg):
    # 這裡請確保 GitHub Secrets 名稱是 TG_TOKEN
    token = os.getenv("TG_TOKEN") 
    if not token:
        print("錯誤：找不到 TG_TOKEN 環境變數")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": 8529293240, 
        "text": msg
    }

    try:
        r = requests.post(url, data=data)
        if r.status_code != 200:
            print(f"發送失敗：{r.text}")
    except Exception as e:
        print(f"發送時發生異常：{e}")

def main():
    res = requests.get(URL, headers=HEADERS)
    if res.status_code != 200:
        print(f"網頁抓取失敗，狀態碼：{res.status_code}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    
    # 嘗試抓取更精確的標籤（BigGo 的商品通常在 div 裡，可以視情況調整）
    items = soup.select("a") 
    print(f"共掃描到 {len(items)} 個連結")

    seen = load_seen()
    new_seen = set(seen)
    count = 0

    for item in items:
        title = item.get_text(strip=True)
        link = item.get("href")

        if not link or "http" not in link:
            continue

        # 加強過濾條件，避免抓到廣告或導覽列
        if "iPhone" in title and "512GB" in title:
            if link not in seen:
                msg = f"🆕 新商品發現！\n名稱：{title}\n連結：{link}"
                send_telegram(msg)
                new_seen.add(link)
                count += 1
                print(f"找到新商品：{title}")

        if count >= 5: # 每次最多推播 5 個，避免洗版
            break

    save_seen(new_seen)
    print("程式執行完畢")

# (其餘 load_seen, save_seen 維持不變)
