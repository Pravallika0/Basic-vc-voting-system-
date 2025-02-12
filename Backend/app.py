from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import qrcode
import base64
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Allow React frontend to communicate with Flask

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

votes_db = {}  # Temporary storage for vote shares

# Function to generate visual cryptography vote shares
def generate_vote_shares(text):
    img = np.full((100, 100), 255, dtype=np.uint8)  # White background
    cv2.putText(img, text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, 0, 2)

    rows, cols = img.shape
    share1 = np.random.randint(0, 2, (rows, cols), dtype=np.uint8) * 255
    share2 = cv2.bitwise_xor(img, share1)

    return share1, share2

# Route to store vote & generate shares
@app.route('/store_vote', methods=['POST'])
def store_vote():
    data = request.json
    voter_id = data['voter_id']
    candidate = data['candidate']

    share1, share2 = generate_vote_shares(candidate[0])  # Encrypt vote

    # Save vote shares
    share1_path = f"uploads/{voter_id}_share1.png"
    share2_path = f"uploads/{voter_id}_share2.png"

    cv2.imwrite(share1_path, cv2.cvtColor(share1, cv2.COLOR_GRAY2BGR))
    cv2.imwrite(share2_path, cv2.cvtColor(share2, cv2.COLOR_GRAY2BGR))


    votes_db[voter_id] = share1_path  # Store only Share 1

    # Generate QR code for voter Share 2
    qr = qrcode.make(f"share2_{voter_id}.png")
    qr_path = f"uploads/{voter_id}_qr.png"
    qr.save(qr_path)

    with open(qr_path, "rb") as file:
        qr_base64 = base64.b64encode(file.read()).decode()

    return jsonify({
        "status": "Vote stored successfully!",
        "qrCode": f"data:image/png;base64,{qr_base64}"
    })


# Route to verify vote (Stacking Shares)
@app.route('/verify_vote', methods=['POST'])
def verify_vote():
    if 'vote_share' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    uploaded_file = request.files['vote_share']
    voter_id = request.form['voter_id']
    
    if voter_id not in votes_db:
        return jsonify({"message": "Vote not found in system"}), 404

    share1_path = votes_db[voter_id]

    # Save uploaded file temporarily
    uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
    uploaded_file.save(uploaded_path)

    print(f"DEBUG: Stored Share 1 Path: {share1_path}")
    print(f"DEBUG: Uploaded Share Path: {uploaded_path}")

    # Load the stored share and uploaded share
    share1 = cv2.imread(share1_path, cv2.IMREAD_GRAYSCALE)
    share2 = cv2.imread(uploaded_path, cv2.IMREAD_GRAYSCALE)

    if share1 is None:
        print("ERROR: Failed to load stored share!")
        return jsonify({"message": "Error reading stored share."}), 500

    if share2 is None:
        print("ERROR: Failed to load uploaded share!")
        return jsonify({"message": "Error reading uploaded share."}), 500

    # Ensure both images are the same size
    if share1.shape != share2.shape:
        print(f"ERROR: Size mismatch! Resizing uploaded share to {share1.shape}")
        share2 = cv2.resize(share2, (share1.shape[1], share1.shape[0]))  # Resize to match share1

    # Stack the uploaded share with stored Share 1
    reconstructed_vote = cv2.bitwise_xor(share1, share2)

    # Save reconstructed vote
    reconstructed_path = f"uploads/{voter_id}_reconstructed.png"
    cv2.imwrite(reconstructed_path, reconstructed_vote)

    print(f"DEBUG: Reconstructed Vote Path: {reconstructed_path}")

    return jsonify({
        "message": "Vote verified successfully!",
        "image": reconstructed_path
    })


if __name__ == '__main__':
    app.run(debug=True)
