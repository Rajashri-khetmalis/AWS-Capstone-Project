from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
import uuid
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "bloodbridge_secret"

# ---------------- AWS CONFIG ----------------
REGION = "us-east-1"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)

SNS_TOPIC_ARN = "aarn:aws:sns:us-east-1:343218180150:Bloodbridger"

# ---------------- TABLES ----------------
users_table = dynamodb.Table("Users")          # Donors
hospitals_table = dynamodb.Table("Hospitals")
admins_table = dynamodb.Table("Admins")
requests_table = dynamodb.Table("BloodRequests")
inventory_table = dynamodb.Table("BloodInventory")

# ---------------- SNS ----------------
def send_notification(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print("SNS Error:", e)

# ---------------- COMMON ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ================== AUTH ==================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        table = users_table if role == "donor" else hospitals_table

        if "Item" in table.get_item(Key={"username": username}):
            flash("User already exists")
            return redirect(url_for("signup"))

        table.put_item(Item={
            "username": username,
            "password": password,
            "role": role
        })

        send_notification("New Signup", f"{role.capitalize()} {username} registered")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        table = users_table if role == "donor" else hospitals_table

        res = table.get_item(Key={"username": username})
        if "Item" in res and res["Item"]["password"] == password:
            session["username"] = username
            session["role"] = role
            return redirect(url_for(f"{role}_dashboard"))

        flash("Invalid Credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================== DONOR ==================

@app.route("/donor/dashboard")
def donor_dashboard():
    if session.get("role") != "donor":
        return redirect(url_for("login"))

    requests = requests_table.scan().get("Items", [])
    return render_template("donor_dashboard.html", requests=requests)

@app.route("/donor/accept/<req_id>", methods=["POST"])
def donor_accept(req_id):
    username = session["username"]

    req = requests_table.get_item(Key={"request_id": req_id})["Item"]
    bg = req["blood_group"]

    # Update request
    requests_table.update_item(
        Key={"request_id": req_id},
        UpdateExpression="SET #s=:s, donor=:d",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "Accepted", ":d": username}
    )

    # Increase inventory
    inv = inventory_table.get_item(Key={"blood_group": bg})
    units = inv.get("Item", {}).get("units", 0) + req["units"]

    inventory_table.put_item(Item={
        "blood_group": bg,
        "units": units
    })

    send_notification("Donation Accepted", f"{username} accepted request {req_id}")
    return redirect(url_for("donor_dashboard"))

# ================== HOSPITAL ==================

@app.route("/hospital/dashboard")
def hospital_dashboard():
    if session.get("role") != "hospital":
        return redirect(url_for("login"))

    username = session["username"]
    requests = requests_table.scan().get("Items", [])
    return render_template("hospital_dashboard.html", requests=requests, username=username)

@app.route("/request_blood", methods=["POST"])
def request_blood():
    request_id = str(uuid.uuid4())

    requests_table.put_item(Item={
        "request_id": request_id,
        "hospital": session["username"],
        "blood_group": request.form["blood_group"],
        "units": int(request.form["units"]),
        "status": "Pending",
        "donor": ""
    })

    send_notification("Blood Request", f"New blood request from hospital")
    return redirect(url_for("hospital_dashboard"))

# ================== ADMIN ==================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        res = admins_table.get_item(Key={"username": username})
        if "Item" in res and res["Item"]["password"] == password:
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    donors = len(users_table.scan().get("Items", []))
    hospitals = len(hospitals_table.scan().get("Items", []))
    requests = requests_table.scan().get("Items", [])
    inventory = inventory_table.scan().get("Items", [])

    return render_template(
        "admin_dashboard.html",
        donors=donors,
        hospitals=hospitals,
        requests=requests,
        inventory=inventory
    )

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

# ================== RUN ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
