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

s3 = boto3.client("s3")
BUCKET_NAME = 'smartparcel-photos-20240004591'

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

    if len(data["sender"]) > 60 or len(data["reciever"]) > 60 or len(data["address"]) > 100:
         return "Error: Too Long"

    parcel_id = str(uuid.uuid4())

    item = {
        "parcel_id": parcel_id,
        "sender": data["sender"], 
        "receiver": data["receiver"],
        "address": data["address"],
	"status": "created",
    }

    try:
        table.put_item(Item=item)

        return jsonify({
            "The parcel id is: ": parcel_id
        }), 201

    except Exception as e:
        return jsonify({
            "error": "ERROR",
            "details": str(e)
        }), 500

#GET Parcel
@app.route("/api/parcels/<parcel_id>", methods = ["GET"])
def get_parcel(parcel_id):
    user = get_user()
	
    if not user:
        return jsonify({"error": "unauthorized access"}), 401
   
    try:
        exists  = table.get_item(Key={"parcel_id": parcel_id})

        if "Item" not in exists:
            return jsonify({"error": "Parcel not found"}), 404

        return jsonify (exists["Item"]), 200

    except Exception as e:
        return jsonify({
            "error": "ERROR",
            "details": str(e)
        }), 500

#Update Parcel Status
@app.route("/api/parcels/<parcel_id>/status", methods = ["PUT"])
def update_parcel(parcel_id):
	user = get_user()
	if user != "driver":
		return jsonify({"error":"Unauthorized access"}), 403

	if not request.is_json:	
		return jsonify({"error": "Request must be JSON"}), 400
	data = request.get_json()

	status = data.get("status")
	parcel_status = ["picked_up", "in_transit", "delivered"]
	
	if not status or status not in parcel_status:
		return jsonify({"error": "Invalid status"}),404

	try:
		exists  = table.get_item(Key={"parcel_id": parcel_id})
	
		if "Item" not in exists:
			return jsonify({"error": "No parcel created"}), 404
	
		table.update_item(
			Key={"parcel_id": parcel_id},
			UpdateExpression= "set #s =  :s",
			ExpressionAttributeNames={"#s": "status"},
			ExpressionAttributeValues={":s": status}
			)
		
		return jsonify({
			"The parcel status has been updated to: ": status
			}),200

	except Exception as e:
		return jsonify({
			"error": "ERROR",
			"details": str(e)
		}), 500
	
#GET List Parcels 
@app.route("/api/parcels", methods = ["GET"])
def list_parcels():
	user = get_user()

	if user != "admin":
		return jsonify({"error": "unauthorized access"}),401
	
	status_filer = request.args.get("status")
	try:
		exists = table.scan()
		items= exists["Items"]

		return jsonify ({
			"count": len(items),
			"parcels" : items
			}), 200
	except:
		return jsonify ({"error": "ERROR"}), 500
			
#DELETE Cancel Parcels 
@app.route("/api/parcels/<parcel_id>", methods = ["DELETE"])
def delete_parcel(parcel_id):
    user = get_user()


    if user != "admin":
        return jsonify({"error": "unauthorized access"}), 401

    try:
        exists = table.get_item(Key={"parcel_id": parcel_id})

        if "Item" not in exists:
            return jsonify({"error": "Parcel has not been created"}), 404

        parcel = exists["Item"]


        if parcel["status"] != "created":
            return jsonify({"error": "Cannot cancel parcel"}), 400

        table.delete_item(Key={"parcel_id": parcel_id})

        return jsonify({"message": "Parcel cancelled"}), 200

    except:
        return jsonify({"error": "ERROR"}), 500

#POST UPLOAD PHOTO
@app.route("/api/parcels/<parcel_id>/photo", methods=["POST"])
def upload_parcel(parcel_id):
     user = get_user()

     if user != "driver":
          return jsonify({"error": "unauthorized access"}), 401
    

     if "photo" not in request.files:
          return jsonify({"error": "There's no photo uploaded"}), 400

     photo = request.files["photo"]

     if "photo" != endswith('.jpg'):
          return "error: Wrong Format"


if __name__ == "__main__":
     app.run(host="0.0.0.0",port=8080)
