# -------------------------------------------------------
# SmartParcel — NET_214 Project, Spring 2026
# Author  : Stephanie Malaiba
# ID      : 20240004591
# Email   : 20240004591 @cud.ac.ae
# AWS Acc : 9432-7344-4306
# -------------------------------------------------------

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
table = dynamodb.Table("notifications")

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#HealthCheck
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "hostname": socket.gethostname()}), 200

