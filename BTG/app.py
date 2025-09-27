from pymongo import MongoClient
from bson import Binary
from datetime import datetime
import io
import os
from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS  # ← Added for React frontend support
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import cv2
import tensorflow as tf

client = MongoClient('mongodb://localhost:27017/')
db = client.brain_tumor_db
scans_collection = db.mri_scans

app = Flask(__name__)
CORS(app)  # ← Allow requests from React (localhost:3000 or Vercel)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB max file size

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load your trained model
MODEL_PATH = 'brain_tumor_model.h5'
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}. Please train it first.")
model = tf.keras.models.load_model(MODEL_PATH)

# Class labels (MUST match training folder names)
class_labels = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_brain_mri_from_bytes(file_bytes):
    """Validate MRI from in-memory bytes (no file save)"""
    try:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False, "Cannot read image"

        h, w = img.shape
        if h < 100 or w < 100:
            return False, "Image too small for MRI"

        edge_pixels = np.concatenate([
            img[0, :], img[-1, :], img[:, 0], img[:, -1]
        ])
        center = img[h//4:3*h//4, w//4:3*w//4]
        if np.mean(center) <= np.mean(edge_pixels) + 10:
            return False, "Does not resemble brain MRI (no bright center)"
        return True, "Valid"
    except Exception as e:
        return False, str(e)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 🔥 NEW: API endpoint for React frontend
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        # Read file into memory (no saving to disk)
        file_bytes = file.read()
        filename = secure_filename(file.filename)

        # Validate MRI from bytes
        is_mri, msg = is_brain_mri_from_bytes(file_bytes)
        if not is_mri:
            return jsonify({'error': msg}), 400

        # Preprocess for model
        img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        predictions = model.predict(img_array)
        pred_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][pred_idx]) * 100
        predicted_class = class_labels[pred_idx]

        # 🧠 STORE IN LOCAL MONGODB
        scan_doc = {
            "filename": filename,
            "image_data": Binary(file_bytes),  # Store as binary
            "prediction": {
                "class": predicted_class.replace('_', ' ').title(),
                "confidence": round(confidence, 2)
            },
            "timestamp": datetime.utcnow()
        }
        result = scans_collection.insert_one(scan_doc)
        
        return jsonify({
            'scan_id': str(result.inserted_id),
            'class': scan_doc['prediction']['class'],
            'confidence': scan_doc['prediction']['confidence']
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

# Existing route for Flask frontend (optional)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file uploaded')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            is_mri, msg = is_brain_mri(file_path)
            if not is_mri:
                os.remove(file_path)
                return render_template('index.html', error=f'Invalid image: {msg}')

            img = Image.open(file_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = model.predict(img_array)
            pred_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][pred_idx]) * 100
            predicted_class = class_labels[pred_idx]

            result = {
                'class': predicted_class.replace('_', ' ').title(),
                'confidence': round(confidence, 2)
            }
            return render_template('index.html', prediction=result, image=filename)

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)