from flask import Flask, request, jsonify, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS

import base64
import json

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://mongodb:27017/")
db = client["productdb"]
collection = db["products"]

def get_user_from_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = token.split('.')[1]
        # corectăm padding-ul base64
        padding = '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        user_data = json.loads(decoded)
        return user_data.get("preferred_username") or user_data.get("email") or user_data.get("sub")
    except Exception as e:
        print("Eroare la decodarea tokenului:", e)
        return None

@app.route("/products", methods=["POST"])
def create_product_entry():
    user_id = get_user_from_token()
    if not user_id:
        return jsonify({"error": "Token lipsă sau invalid"}), 401

    product_data = request.get_json()
    if not product_data:
        return jsonify({"error": "Product info is required"}), 400

    product_data["user_id"] = user_id  # asociezi produsul cu userul logat
    result = collection.insert_one(product_data)

    return jsonify({"_id": str(result.inserted_id)}), 201


@app.route("/products/<int:user_id>/<_id>", methods=["GET"])
def get_product_(user_id, _id):

    product = collection.find_one({"_id": ObjectId(_id), "user_id": user_id})

    if product is None:
        return jsonify({"error": "Product not found", "user_id": user_id, "_id": _id}), 404
    
    product["_id"] = str(product["_id"]) # _id is of type ObjectId that can't be serialized to json
    return jsonify(product), 200


@app.route("/products", methods=["GET"])
def get_products_by_token():
    user_id = get_user_from_token()
    if not user_id:
        return jsonify({"error": "User neautentificat sau token invalid"}), 401

    # 🔍 Preluăm parametrii query
    search = request.args.get("search", "")
    sort_key = request.args.get("sort", "name")
    sort_order = request.args.get("order", "asc")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 100))

    # 🔍 Construim query Mongo
    query = {"user_id": user_id}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    # ⬇️ Sortare Mongo
    from pymongo import ASCENDING, DESCENDING
    order = ASCENDING if sort_order == "asc" else DESCENDING

    # 📄 Skip + limit pentru paginare
    skip = (page - 1) * limit

    # 🔁 Execută query
    cursor = collection.find(query).sort(sort_key, order).skip(skip).limit(limit)

    products = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        products.append(p)

    return jsonify(products), 200


@app.route("/products/<int:user_id>/<_id>", methods=["PATCH"])
def update_product(user_id, _id):
    change_data = request.get_json()

    result = collection.update_one(
        {"_id": ObjectId(_id), "user_id": user_id},
        {"$set": change_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product updated successfully"}), 200

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    user_id = get_user_from_token()
    if not user_id:
        return jsonify({"error": "Token lipsă sau invalid"}), 401

    try:
        result = collection.delete_one({
            "_id": ObjectId(product_id),
            "user_id": user_id
        })

        if result.deleted_count == 0:
            return jsonify({"error": "Produsul nu a fost găsit sau nu-ți aparține"}), 404

        return jsonify({"message": "Produs șters cu succes"}), 200

    except Exception as e:
        print("Eroare la ștergere:", e)
        return jsonify({"error": "Eroare internă la ștergere"}), 500



@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
