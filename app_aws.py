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

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:343218180150:Bloodbridger"

# ---------------- TABLES ----------------
users_table = dynamodb.Table("Users")          # PK: username
hospitals_table = dynamodb.Table("Hospitals")  # PK: username
admins_table = dynamodb.Table("Admins")        # PK: username
requests_table = dynamodb.Table("BloodRequests")   # PK: request_id
inventory_table = dynamodb.Table("BloodInventory") # PK: blood_group

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

# ================== HOME ==================

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/index')

def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
# ================== AUTH ==================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        table = users_table if role == "donor" else hospitals_table

        res = table.get_item(Key={"username": username})
        if res.get("Item"):
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

        if role == "admin":
            table = admins_table
        elif role == "donor":
            table = users_table
        else:
            table = hospitals_table

        res = table.get_item(Key={"username": username})
        if res.get("Item") and res["Item"]["password"] == password:
            session.clear()
            session["username"] = username
            session["role"] = role

            if role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif role == "donor":
                return redirect(url_for("donor_dashboard"))
            else:
                return redirect(url_for("hospital_dashboard"))

        flash("Invalid Credentials")

    return render_template("login.html")



# ================== DONOR ==================
@app.route("/donor/dashboard")
def donor_dashboard():
    if session.get("role") != "donor":
        return redirect(url_for("login"))

    requests = requests_table.scan().get("Items", [])
    return render_template(
        "donor_dashboard.html",
        username=session["username"],
        requests=requests
    )

@app.route("/donor/accept/<req_id>", methods=["POST"])
def donor_accept(req_id):
    if session.get("role") != "donor":
        return redirect(url_for("login"))

    username = session["username"]
    req = requests_table.get_item(Key={"request_id": req_id}).get("Item")

    if not req:
        flash("Request not found")
        return redirect(url_for("donor_dashboard"))

    bg = req["blood_group"]

    requests_table.update_item(
        Key={"request_id": req_id},
        UpdateExpression="SET #s=:s, donor=:d",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "Accepted", ":d": username}
    )

    inv = inventory_table.get_item(Key={"blood_group": bg}).get("Item")
    current_units = inv["units"] if inv else 0

    inventory_table.put_item(Item={
        "blood_group": bg,
        "units": current_units + int(req["units"])
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

    return render_template(
        "hospital_dashboard.html",
        username=username,
        requests=requests
    )
@app.route("/request_blood", methods=["POST"])
def request_blood():
    if session.get("role") != "hospital":
        return redirect(url_for("login"))

    request_id = str(uuid.uuid4())

    requests_table.put_item(Item={
        "request_id": request_id,
        "hospital": session["username"],
        "blood_group": request.form["blood_group"],
        "units": int(request.form["units"]),
        "status": "Pending",
        "donor": ""
    })
    send_notification("Blood Request", "New blood request created")
    return redirect(url_for("hospital_dashboard"))

# ================== ADMIN ==================
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    donors = users_table.scan().get("Items", [])
    hospitals = hospitals_table.scan().get("Items", [])
    requests = requests_table.scan().get("Items", [])
    inventory = inventory_table.scan().get("Items", [])

    return render_template(
        "admin_dashboard.html",
        donors=len(donors),
        hospitals=len(hospitals),
        requests=requests,
        inventory={i["blood_group"]: i["units"] for i in inventory}
    )

# ================== RUN ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
