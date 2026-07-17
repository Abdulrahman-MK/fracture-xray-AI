import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from ultralytics import YOLO

# Configuration
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_PATH = 'models/best.pt'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.secret_key = 'your-secret-key'  # for flashing messages

# Load model once
model = YOLO(MODEL_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_and_annotate(image_path):
    # Run inference
    results = model(image_path)
    # results[0] is the first image result
    result = results[0]
    # Get annotated image (numpy array with boxes)
    annotated_img = result.plot()  # BGR format
    # Save annotated image
    basename = os.path.basename(image_path)
    result_filename = 'res_' + basename
    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    cv2.imwrite(result_path, annotated_img)
    
    # Extract detection info
    boxes = result.boxes
    if boxes is not None and len(boxes) > 0:
        # Take the highest confidence detection
        conf = boxes.conf[0].item()
        cls = int(boxes.cls[0].item())
        # Class name (assuming only one class)
        class_name = model.names[cls]  # 'fracture'
        detection_status = f"Fracture Detected"
        confidence = f"{conf*100:.2f}%"
        # Optionally, you can get bounding box coordinates to estimate location
        # but for simplicity we skip location.
        location = "Distal Radius"  # Placeholder – you could add logic based on coordinates
    else:
        detection_status = "No Fracture Detected"
        confidence = "N/A"
        location = "N/A"
    
    return {
        'result_path': result_filename,
        'detection_status': detection_status,
        'confidence': confidence,
        'location': location
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Run prediction
            prediction = predict_and_annotate(filepath)
            
            # ---------- FIX APPLIED HERE ----------
            original_path = f"uploads/{filename}"
            result_path = f"results/{prediction['result_path']}"
            # --------------------------------------
            
            return render_template('result.html', 
                                   original_path=original_path,
                                   result_path=result_path,
                                   status=prediction['detection_status'],
                                   confidence=prediction['confidence'],
                                   location=prediction['location'])
        else:
            flash('Allowed file types: png, jpg, jpeg')
            return redirect(request.url)
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)