import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from bson.objectid import ObjectId
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import jsonify

# Load environment variables
load_dotenv()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")  # ✅ Corrected this line
client = MongoClient(MONGO_URI)
db = client['gotouge_bot']
quotes_col = db['quotes']

# Cloudinary Setup
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Flask Setup
app = Flask(__name__)

@app.route('/')
def index():
    quotes = list(quotes_col.find())
    return render_template('index.html', quotes=quotes)

@app.route('/add', methods=['POST'])
def add():
    text = request.form['text']
    image_url = request.form.get('image')
    image_file = request.files.get('upload')
    
    if image_file and image_file.filename:
        # Upload to Cloudinary instead of saving locally
        result = cloudinary.uploader.upload(image_file)
        image_url = result.get('secure_url')  # Get the Cloudinary-hosted image URL

    quotes_col.insert_one({"text": text, "image": image_url})
    return redirect('/')

@app.route('/delete/<id>')
def delete(id):
    quotes_col.delete_one({"_id": ObjectId(id)})
    return redirect('/')

@app.route('/quote/<id>')
def get_quote(id):
    quote = quotes_col.find_one({"_id": ObjectId(id)})
    if not quote:
        return jsonify({"error": "Quote not found"}), 404
    return jsonify({
        "id": str(quote["_id"]),
        "text": quote["text"],
        "image": quote.get("image", "")
    })

@app.route('/update/<id>', methods=['POST'])
def update_quote(id):
    text = request.form['text']
    image_url = request.form.get('image')  # Image URL field
    image_file = request.files.get('upload')  # Uploaded file

    # Upload new image if a file is selected
    if image_file and image_file.filename:
        result = cloudinary.uploader.upload(image_file)
        image_url = result.get('secure_url')

    # Update the document
    quotes_col.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"text": text, "image": image_url}}
    )
    return redirect('/')

def start_flask_server():
    port = int(os.environ.get("PORT", 5000))  # ✅ Use Heroku PORT env
    app.run(host='0.0.0.0', port=port)
