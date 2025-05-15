from flask import Flask, request, jsonify, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://mongodb:27017/")
db = client["productdb"]
collection = db["products"]

@app.route("/products", methods=["POST"])
def create_product_entry():
    product_data = request.get_json()

    if not product_data:
        return jsonify({"error": "Product info is required"}), 400

    result = collection.insert_one(product_data)

    return jsonify({"_id": result.inserted_id}), 201


@app.route("/products/<int:user_id>/<_id>", methods=["GET"])
def get_product_(user_id, _id):

    product = collection.find_one({"_id": ObjectId(_id), "user_id": user_id})

    if product is None:
        return jsonify({"error": "Product not found", "user_id": user_id, "_id": _id}), 404
    
    product["_id"] = str(product["_id"]) # _id is of type ObjectId that can't be serialized to json
    return jsonify(product), 200


@app.route("/products/<int:user_id>", methods=["GET"])
def get_products_by_user(user_id):
    products = list(collection.find({"user_id": user_id}))

    if not products:
        return jsonify({"message": "No products found for this user."}), 404

    for product in products:
        product["_id"] = str(product["_id"])

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

@app.route("/products/<int:user_id>/<_id>", methods=["DELETE"])
def delete_product(user_id, _id):
    result = collection.delete_one({"_id": ObjectId(_id), "user_id": user_id})

    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted successfully"}), 200

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
