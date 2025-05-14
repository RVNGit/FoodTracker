from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://mongodb:27017/")
db = client["productdb"]
collection = db["products"]

def get_user_id():
     return 1

def get_product_from_openfoodfacts(barcode):
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        data = response.json()
        if "product" not in data:
            return None

        product = data["product"]
        result = {
            'name': product.get('product_name', 'N/A'),
            'quantity': product.get('quantity', 'N/A'),
            'ingredients': product.get('ingredients_text', 'N/A'),
            'nutriments': {
                'calories': product.get('nutriments', {}).get('energy-kcal_100g', 'N/A'),
                'proteins': product.get('nutriments', {}).get('proteins_100g', 'N/A'),
                'fat': product.get('nutriments', {}).get('fat_100g', 'N/A'),
                'sugars': product.get('nutriments', {}).get('sugars_100g', 'N/A'),
                'salt': product.get('nutriments', {}).get('salt_100g', 'N/A'),
            },
            'image': product.get('image_front_url', 'N/A'),
            'message': 'N/A'
        }

        return result

def get_product_info(barcode, expiry_date, name, quantity):
    result = get_product_from_openfoodfacts(barcode)
    if result is None:
        result = {'message': 'Could not retrieve product information from Open Food Facts.'}
    
    result['barcode'] = barcode
    result['user_id'] = get_user_id()

    if not expiry_date:
        expiry_date = 'N/A'
    result['expiry_date'] = expiry_date

    if name:
        result['name'] = name
    if quantity:
        result['quantity'] = quantity

    return result

@app.route("/api/product/add", methods=["POST"])
def create_product_entry():
    data = request.get_json()
    barcode = data.get("barcode")

    if not barcode:
        return jsonify({"error": "Barcode is required"}), 400
    
    product_data = get_product_info(barcode=barcode, expiry_date=data.get("expiry_date"), name=data.get("name"), quantity=data.get("quantity"))
    collection.insert_one(product_data)

    return jsonify({"message": "Product added successfully"}), 201


@app.route("/api/product/get", methods=["GET"])
def get_product_():
    product_id = request.args.get("_id")

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    user_id = get_user_id() 
    product = collection.find_one({"_id": ObjectId(product_id), "user_id": user_id})

    if product is None:
        return jsonify({"error": "Product not found"}), 404
    
    product["_id"] = str(product["_id"]) # _id is of type ObjectId that can't be serialized to json
    return product, 200


@app.route("/api/product/update", methods=["PATCH"])
def update_product():
    data = request.get_json()
    product_id = data.get("_id")

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    update_fields = {}
    if "name" in data:
        update_fields["name"] = data["name"]
    if "expiry_date" in data:
        update_fields["expiry_date"] = data["expiry_date"]
    if "quantity" in data:
        update_fields["quantity"] = data["quantity"]

    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    result = collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product updated successfully"}), 200

@app.route("/api/product/delete", methods=["DELETE"])
def delete_product():
    data = request.get_json()
    product_id = data.get("_id")

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    result = collection.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
