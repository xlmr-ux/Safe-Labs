from flask import Flask, request, jsonify
import boto3
import os

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    """Handle file encryption."""
    return handle_file_operation('encrypt')

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    """Handle file decryption."""
    return handle_file_operation('decrypt')

@app.route('/upload/<provider>', methods=['POST'])
def upload_to_cloud(provider):
    """Handle file uploads to the specified cloud provider."""
    if provider not in ['gcp', 'aws']:
        return jsonify({'error': 'Invalid cloud provider selected.'}), 400
    return handle_cloud_upload(provider)

def handle_file_operation(operation):
    """Perform encryption or decryption on the uploaded file."""
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file uploaded. Ensure it is a valid type.'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Placeholder for actual encryption/decryption logic
    return jsonify({'message': f'{operation.capitalize()} operation completed successfully.', 'file_path': file_path}), 200

def handle_cloud_upload(provider):
    """Upload file to the specified cloud provider."""
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file uploaded. Ensure it is a valid type.'}), 400

    if provider == 'aws':
        return upload_to_aws(file)
    elif provider == 'gcp':
        # Placeholder for Google Cloud upload
        return jsonify({'message': 'Google Cloud upload feature coming soon!'}), 200

def upload_to_aws(file):
    """Upload a file to AWS S3."""
    s3 = boto3.client('s3')
    bucket_name = 'your-bucket-name'
    file_key = file.filename

    try:
        s3.upload_fileobj(file, bucket_name, file_key)
        return jsonify({'message': f'File successfully uploaded to AWS S3 as {file_key}.'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to upload to AWS S3: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
