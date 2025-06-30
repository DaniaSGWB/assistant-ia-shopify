import os
import openai
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHOPIFY_ADMIN_API_KEY = os.getenv("SHOPIFY_ADMIN_API_KEY")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
HEADERS_SHOPIFY = {
    "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_KEY,
    "Content-Type": "application/json"
}

openai.api_key = OPENAI_API_KEY

def get_products():
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/products.json"
    response = requests.get(url, headers=HEADERS_SHOPIFY)
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        return []

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    products = get_products()
    product_info = "\n".join([f"- {p['title']} : {p['body_html']}" for p in products[:3]])

    prompt = f"Tu es un assistant pour une boutique Shopify. Voici quelques produits :\\n{product_info}\\n\\nSi le client cherche un produit sans être précis, pose-lui quelques questions pour cerner ses besoins, puis recommande un produit adapté.\\n\\nClient : {user_input}\\nAssistant :"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant amical et professionnel pour une boutique en ligne."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
