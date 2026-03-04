from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/get_price')
def get_price():
    target_url = request.args.get('url')
    # Headers make the request look like a real mobile browser to avoid blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "en-IN,en;q=0.9"
    }
    
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Real-time extraction for Amazon India
        name = soup.select_one("#productTitle").get_text().strip()
        # Clean price string to get just the numbers
        price_raw = soup.select_one(".a-price-whole").get_text().replace(',', '').replace('.', '')
        img = soup.select_one("#landingImage")['src']

        return jsonify({
            "status": "success",
            "name": name[:60] + "...",
            "price": price_raw,
            "image": img,
            "recommendation": "BUY" if int(price_raw) < 70000 else "WAIT" 
        })
    except Exception as e:
        return jsonify({"status": "error", "message": "Product details not found. Please check the link."})

if __name__ == "__main__":
    app.run()
