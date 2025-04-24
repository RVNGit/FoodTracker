from flask import Flask, request, jsonify
import requests
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Metrici Prometheus
REQUEST_COUNT = Counter('api_requests_total', 'Total number of API requests', ['endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Duration of API requests in seconds', ['endpoint'])

@app.route("/api/product", methods=["GET"])
def get_product():
    with REQUEST_DURATION.labels(endpoint="/api/product").time():
        REQUEST_COUNT.labels(endpoint="/api/product").inc()

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
            'brands': product.get('brands', 'N/A'),
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
            'nutriscore': product.get('nutriscore_grade', 'N/A'),
            'nova_group': product.get('nova_group', 'N/A'),
            'ecoscore': product.get('ecoscore_grade', 'N/A'),
            'image': product.get('image_front_url', 'N/A')
        }

        return jsonify(result)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
