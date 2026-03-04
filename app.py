from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app) # This allows AppCreator24 to talk to your server

def scrape_amazon(soup):
    try:
        name = soup.select_one("#productTitle").get_text().strip()
        price = soup.select_one(".a-price-whole").get_text().replace(',', '').replace('.', '')
        img = soup.select_one("#landingImage")['src']
        return name, price, img
    except: return None, None, None

def scrape_flipkart(soup):
    try:
        # Flipkart often changes classes; these are the most stable ones for 2026
        name = soup.select_one(".B_NuCI").get_text().strip()
        price = soup.select_one("._30jeq3._16Jk6d").get_text().replace('₹', '').replace(',', '')
        img = soup.select_one("._396cs4._2amPTt._3qGedV")['src']
        return name, price, img
    except: return None, None, None

@app.route('/get_price')
def get_price():
    target_url = request.args.get('url')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9"
    }
    
    try:
        res = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        if "amazon.in" in target_url:
            name, price, img = scrape_amazon(soup)
            store = "Amazon"
        elif "flipkart.com" in target_url:
            name, price, img = scrape_flipkart(soup)
            store = "Flipkart"
        else:
            return jsonify({"status": "error", "message": "Only Amazon India & Flipkart are supported."})

        if not name or not price:
            return jsonify({"status": "error", "message": "Could not extract details. Website might be blocking us."})

        return jsonify({
            "status": "success",
            "name": name[:50] + "...",
            "price": price,
            "image": img,
            "store": store,
            "recommendation": "BUY" if int(price) < 50000 else "WAIT" 
        })
    except Exception as e:
        return jsonify({"status": "error", "message": "Server Busy. Try again in 10 seconds."})

if __name__ == "__main__":
    app.run()
