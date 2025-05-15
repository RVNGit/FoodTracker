from flask import Flask, request, jsonify, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

CRUD_SERVICE_URL = "http://crud:5000"
OPENFOODFACTS_SERVICE_URL = "http://openfoodfacts:5000"
USER_FIELD = "user_id"

def get_user_id():
    return 1

# methods for interaction with the microservice for the database handling
def add_product_to_db(product_data):
    response = requests.post(f"{CRUD_SERVICE_URL}/products", json=product_data)
    return response.json(), response.status_code

def get_product_from_db(_id):
    response = requests.get(f"{CRUD_SERVICE_URL}/products/{get_user_id()}/{_id}")
    return response.json(), response.status_code

def get_all_user_products_from_db():
    response = requests.get(f"{CRUD_SERVICE_URL}/products/{get_user_id()}")
    return response.json(), response.status_code

def update_product_in_db(_id, change_data):
    if not change_data:
        return {"error": "No fields to update."}, 400

    response = requests.patch(f"{CRUD_SERVICE_URL}/products/{get_user_id()}/{_id}", json=change_data)
    return response.json(), response.status_code

def delete_product_from_db(_id):
    response = requests.delete(f"{CRUD_SERVICE_URL}/products/{get_user_id()}/{_id}")
    return response.json(), response.status_code

# methods for creating a new product
def get_product_from_openfoodfacts(barcode):
    params = {'barcode': barcode}
    response = requests.get(f"{OPENFOODFACTS_SERVICE_URL}/api/product", params=params)
    return response.json(), response.status_code


def get_product_info(barcode, expiry_date, name, quantity):
    result, status = get_product_from_openfoodfacts(barcode)
    if status != 200:
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

# methods for handling requests related to creating, updating or viewing the products
@app.route("/logic/product", methods=["POST"])
def create_product_entry():
    data = request.get_json()
    barcode = data.get("barcode")

    if not barcode:
        return jsonify({"error": "Barcode is required"}), 400
    
    product_data= get_product_info(barcode=barcode, expiry_date=data.get("expiry_date"), name=data.get("name"), quantity=data.get("quantity"))

    result, status = add_product_to_db(product_data=product_data)
    return jsonify(result), status


@app.route("/logic/product/<_id>", methods=["GET"])
def get_product(_id):
    result, status = get_product_from_db(_id=_id)

    if status != 200:
        return result, status
    
    result["status"] = get_product_status(result)
    return jsonify(result), status

@app.route("/logic/product/<_id>", methods=["PATCH"])
def update_product(_id):
    data = request.get_json()

    change_data = {}
    if "name" in data:
        change_data["name"] = data["name"]
    if "expiry_date" in data:
        change_data["expiry_date"] = data["expiry_date"]
    if "quantity" in data:
        change_data["quantity"] = data["quantity"]

    result, status = update_product_in_db(_id=_id, change_data=change_data)
    return jsonify(result), status

@app.route("/logic/product/<_id>", methods=["DELETE"])
def delete_product(_id):
    data = request.get_json()

    result, status = delete_product_from_db(_id=_id)
    return jsonify(result), status

@app.route("/logic/user-products", methods=["GET"])
def get_user_products():
    result, status = get_all_user_products_from_db()

    if status != 200:
        return result, status
    
    for product in result:
        product['status'] = get_product_status(product)

    # if sorting is required
    sort_key = request.args.get('sort')
    if sort_key == 'expiry_date':
        result = sorted(result, key=get_expiry_date_for_sort)

    return jsonify(result), status

def get_expiry_date_for_sort(product_data):
    expiry_date = product_data['expiry_date']
    if not expiry_date or expiry_date == 'N/A':
        return datetime.max
    
    return datetime.strptime(expiry_date, "%Y-%m-%d").date()

# method for the app functionality of highlighting expiring products
def get_product_status(product_data):
    expiry_date = product_data['expiry_date']
    if not expiry_date or expiry_date == 'N/A':
        return 'unknown'
    
    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    today = datetime.today().date()

    if expiry_date < today:
        return 'expired'
    
    diff = relativedelta(expiry_date, today)
    if diff.years == 0 and diff.months == 0 and diff.days < 3:
        return 'expiring soon'
    
    return 'good'

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
