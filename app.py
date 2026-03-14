import os
from flask import Flask, request, jsonify, render_template, url_for

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'media' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['media']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        url = url_for('static', filename='uploads/' + file.filename)
        
        return jsonify({"message": "Success", "url": url, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)