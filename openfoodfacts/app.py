from flask import Flask, request, jsonify, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/api/product", methods=["GET"])
def get_product():
        barcode = request.args.get("barcode")
        if not barcode:
            return jsonify({"error": "Barcode is required"}), 400

        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch product"}), 500

        data = response.json()
        if "product" not in data:
            return jsonify({"error": "Product not found"}), 404

        product = data["product"]
        result = {
            'name': product.get('product_name', 'N/A'),
            'quantity': product.get('quantity', 'N/A'),
            'categories': product.get('categories', 'N/A'),
            'ingredients': product.get('ingredients_text', 'N/A'),
            'nutriments': {
                'calories': product.get('nutriments', {}).get('energy-kcal_100g', 'N/A'),
                'proteins': product.get('nutriments', {}).get('proteins_100g', 'N/A'),
                'fat': product.get('nutriments', {}).get('fat_100g', 'N/A'),
                'sugars': product.get('nutriments', {}).get('sugars_100g', 'N/A'),
                'salt': product.get('nutriments', {}).get('salt_100g', 'N/A'),
            },
            'image': product.get('image_front_url', 'N/A')
        }

        return jsonify(result), 200

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)