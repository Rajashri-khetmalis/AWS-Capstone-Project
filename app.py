from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "bloodbridge"

# -----------------------------
# TEMP STORAGE (Replace with DynamoDB later)
# -----------------------------
blood_requests = []
donors = []
hospitals = []
users = []



blood_inventory = {
    "A+": 0, "A-": 0,
    "B+": 0, "B-": 0,
    "O+": 0, "O-": 0,
    "AB+": 0, "AB-": 0
}

# -----------------------------
# DASHBOARD ROUTER
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "hospital":
        return redirect(url_for("hospital_dashboard"))
    elif role == "admin":
        return redirect(url_for("admin_dashboard"))
    else:
        return redirect(url_for("donor_dashboard"))

# -----------------------------
# BASIC PAGES
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        for user in users:
            if (
                user["username"] == username and
                user["password"] == password and
                user["role"] == role
            ):
                session["username"] = username
                session["role"] = role
                return redirect(url_for("dashboard"))

        # If no match found
        return "  User Not exist Please register first ..Invalid username / password ❌"

    return render_template("login.html")


# -----------------------------
# SIGNUP
# -----------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # check if user already exists
        for user in users:
            if user['username'] == username:
                return "User already exists ❌"

        user = {
            "username": username,
            "password": password,
            "role": role
        }

        users.append(user)

        session['username'] = username
        session['role'] = role

        return redirect(url_for("dashboard"))

    return render_template('signup.html')

# -----------------------------
# DONOR MODULE
# -----------------------------
@app.route("/donor-dashboard")
def donor_dashboard():
    if session.get("role") != "donor":
        return redirect(url_for("login"))

    return render_template(
    "donor_dashboard.html",
    username=session["username"],
    requests=blood_requests
)


# -----------------------------
# HOSPITAL MODULE
# -----------------------------
@app.route("/hospital-dashboard")
def hospital_dashboard():
    if session.get("role") != "hospital":
        return redirect(url_for("login"))

    hospital_requests = [
        r for r in blood_requests
        if r["hospital"] == session["username"]
    ]

    return render_template(
    "hospital_dashboard.html",
    username=session["username"],
    requests=hospital_requests,
    inventory=blood_inventory
)

# -----------------------------
# ADMIN MODULE
# -----------------------------
@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    donor_count = len([u for u in users if u["role"] == "donor"])
    hospital_count = len([u for u in users if u["role"] == "hospital"])

    total_requests = len(blood_requests)
    accepted_requests = len([r for r in blood_requests if r["status"] == "Accepted"])
    pending_requests = len([r for r in blood_requests if r["status"] == "Pending"])

    return render_template(
    "admin_dashboard.html",
    donors=len(donors),
    hospitals=len(hospitals),
    requests=blood_requests,
    total_requests=total_requests,
    accepted_requests=accepted_requests,
    pending_requests=pending_requests,
    inventory=blood_inventory
)



# -----------------------------
# SEARCH BLOOD (DONOR)
# -----------------------------
@app.route('/search_blood', methods=['GET', 'POST'])
def search_blood():
    if request.method == 'POST':
        blood_group = request.form.get('blood_group')

        matched_requests = [
            r for r in blood_requests
            if r["blood_group"] == blood_group
        ]

        return render_template(
            'blood_requests.html',
            blood_group=blood_group,
            requests=matched_requests
        )

    return redirect(url_for("donor_dashboard"))


# -----------------------------
# DONOR ACCEPT REQUEST

@app.route("/donor_accept/<int:req_id>", methods=["POST"])
def donor_accept(req_id):
    if session.get("role") != "donor":
        return redirect(url_for("login"))

    if req_id < len(blood_requests):
       blood_requests[req_id]["status"] = "Donor Accepted"
       blood_requests[req_id]["donor"] = session["username"]

       # 🔥 ADD INVENTORY
       bg = blood_requests[req_id]["blood_group"]
       units = int(blood_requests[req_id]["units"])

       blood_inventory[bg] += units

    return redirect(url_for("donor_dashboard"))
 
# -----------------------------
# REQUEST BLOOD (HOSPITAL) ✅ FIXED
# -----------------------------
@app.route("/request_blood", methods=["POST"])
def request_blood():
    if session.get("role") != "hospital":
        return redirect(url_for("login"))

    request_data = {
    "hospital": session["username"],
    "blood_group": request.form["blood_group"],
    "units": request.form["units"],
    "status": "Pending",
    "donor": None
}


    blood_requests.append(request_data)
    return redirect(url_for("hospital_dashboard"))

# -----------------------------
# ADMIN: ACCEPT / REJECT REQUEST
# -----------------------------
@app.route("/update_request/<int:index>/<action>")
def update_request(index, action):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    if index < len(blood_requests):
        if action == "accept":
         bg = blood_requests[index]["blood_group"]
         units = int(blood_requests[index]["units"])

    # Only accept if stock is available
    if blood_inventory[bg] >= units:
        blood_inventory[bg] -= units
        blood_requests[index]["status"] = "Accepted"
    else:
        blood_requests[index]["status"] = "Rejected"


    return redirect(url_for("admin_dashboard"))




# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
