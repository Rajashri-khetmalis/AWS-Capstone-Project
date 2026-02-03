
### AWS CAPSTONE PROJECT
#  Blood Bank Management System (Flask + AWS)

A full-stack Blood Bank Management System built using **Flask** with **AWS services** integration.  
The system enables **Donors**, **Hospitals**, and **Admins** to interact efficiently for real-time blood request handling.

---

##  Features

###  User Roles
- **Donor**
  - Register & Login
  - View pending blood requests
  - Accept donation requests

- **Hospital**
  - Register & Login
  - Create blood requests
  - Track request status

- **Admin**
  - Dashboard with analytics
  - View total donors, hospitals, and requests
  - Approve / Reject blood requests
  - Assign donors

---

###  AWS Integration
- **DynamoDB**
  - Users Table
  - Blood Requests Table
  - Donors Table
  - Hospitals Table
- **SNS**
  - Notifications on signup, login, request approval

---

###  Inventory Ready (Future-Ready)
- Blood stock logic integrated
- Expandable for real-time inventory tracking

---

##  Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS,JS
- **Database**: AWS DynamoDB
- **Roles**: AWS AWS IAM
- **Notifications**: AWS SNS
- **Cloud**: AWS EC2 (Deployment Phase)

---

##  Project Structure
BLOOD_BRIDGE/
│
├── app.py # Local version (in-memory storage)
├── app_aws.py # AWS production version (DynamoDB + SNS)
├── test_app_aws.py # Local testing using mocked AWS services
├── requirements.txt
├── README.md
│
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── signup.html
│ ├── donor_dashboard.html
│ ├── hospital_dashboard.html
│ ├── admin_dashboard.html
│ ├── navbar.html
│ └── footer.html
│
├── static/
│ ├── style.css
│ └── images/
│
└── screenshots/ # Optional (UI screenshots for GitHub)


##  Installation

### 1️ Clone Repository
git clone <your-github-repo-url>
cd blood-bank-management

### 2️ Install Dependencies
pip install -r requirements.txt

### 3. Running the Application
Local Version (No AWS)
python app.py

### AWS Version (Mocked Services)
python test_app_aws.py

## Access:

http://localhost:5000


### AWS Deployment 


## Steps:


1. Attach IAM Role:

2. AmazonDynamoDBFullAccess

3. AmazonSNSFullAccess

4. Attach SNS 

5. Clone GitHub repo

6. Launch EC2 instance


Run:

python app_aws.py


## Future Enhancements

-- Real-time blood inventory dashboard

-- SMS alerts via SNS

-- Location-based donor search

-- Role-based access control


### Author

## Rajashri Khetmalis
Computer Engineering | Full-Stack | Cloud | AWS