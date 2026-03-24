# -------------------------------------------------------
# SmartParcel — NET_214 Project, Spring 2026
# Author  : Stephanie Malaiba
# ID      : 20240004591
# Email   : 20240004591 @cud.ac.ae
# AWS Acc : 9432-7344-4306
# -------------------------------------------------------

from flask import Flask, request, jsonify
import boto3
import uuid 
from datetime import datetime 
import socket 

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
table = dynamodb.Table("smartparcel-parcels")

#User-Authentication
def get_user():
    return request.headers.get("User")

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#HealthCheck
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "hostname": socket.gethostname()}), 200


#POST: CREATE PARCEL 
@app.route("/api/parcels", methods =["POST"])
def create_parcel():
    user = get_user()

    if user != "driver" and user != "admin":
        return jsonify({"error": "unauthorized access"}), 401

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    if "sender" not in data or "receiver" not in data or "address" not in data:
        return jsonify({"error": "Missing fields"}), 400

    parcel_id = str(uuid.uuid4())

    item = {
        "parcel_id": parcel_id,
        "sender": data["sender"], 
        "receiver": data["receiver"],
        "address": data["address"],
        "status": "created",
        "created_at": current_time()
    }

    try:
        table.put_item(Item=item)

        return jsonify({
            "message": "Parcel created",
            "parcel_id": parcel_id
        }), 201

    except Exception as e:
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500
 
if __name__ == "__main__":
     app.run(host="0.0.0.0",port=8080)
