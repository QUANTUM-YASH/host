from flask import Flask, render_template, request, redirect, Response
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import hashlib
import os

app = Flask(__name__)

# ------------------ MONGODB ------------------
MONGO_URL = "mongodb+srv://sonamsomkar57_db_user:klkzIvKCuh4fNe6H@cluster0.u1quo2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URL)
db = client["portfolio_db"]
projects_collection = db["projects"]

# ------------------ CLOUDINARY ------------------
cloudinary.config(
    cloud_name="dkaikxjzf",
    api_key="422325743576946",
    api_secret="kZd5oQJyNz8p2nJEVa8fE7nVCVQ"
)

# ------------------ PASSWORD SETUP ------------------
# Automatically hash your real password
REAL_PASSWORD = "#yash19-portfolio@"
HASHED_PASSWORD = hashlib.sha256(REAL_PASSWORD.encode()).hexdigest()

def check_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == HASHED_PASSWORD

def authenticate():
    return Response(
        "Access Denied", 401,
        {"WWW-Authenticate": 'Basic realm="Admin Access"'}
    )

# ------------------ HOME ------------------
@app.route("/")
def index():
    try:
        projects = list(projects_collection.find())
        for project in projects:
            project["_id"] = str(project["_id"])
    except Exception as e:
        print("ERROR:", e)
        projects = []

    return render_template("index.html", projects=projects)

# ------------------ ADMIN ------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    auth = request.authorization

    if not auth or not check_password(auth.password):
        return authenticate()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        link = request.form.get("link")
        image = request.files.get("image")

        image_url = ""

        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result["secure_url"]

        project = {
            "title": title,
            "description": description,
            "link": link,
            "image": image_url
        }

        projects_collection.insert_one(project)

        return redirect("/")

    return render_template("admin.html")

# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)
