from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper Functions
def allowed_file(filename):
    """Check if the file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_file(file_path):
    """Encrypt a file and save the encrypted version."""
    key = Fernet.generate_key()  # Generate encryption key
    cipher = Fernet(key)

    # Read the file's contents
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Encrypt the data
    encrypted_data = cipher.encrypt(file_data)

    # Save the encrypted file
    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

    return encrypted_file_path, key

def decrypt_file(file_path, key):
    """Decrypt an encrypted file using the provided key."""
    cipher = Fernet(key)

    # Read the encrypted file's contents
    with open(file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_data)

    # Save the decrypted file
    decrypted_file_path = file_path.replace('.enc', '')
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

    return decrypted_file_path

# Routes
@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    """Handle file encryption."""
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file uploaded. Ensure it is a valid type.'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)  # Save the uploaded file

    try:
        encrypted_file_path, key = encrypt_file(file_path)
        return jsonify({
            'message': 'File encrypted successfully.',
            'encrypted_file_path': encrypted_file_path,
            'key': key.decode()  # Return the encryption key as a string
        }), 200
    except Exception as e:
        return jsonify({'error': f'Encryption failed: {str(e)}'}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    """Handle file decryption."""
    file = request.files.get('file')
    key = request.form.get('key')  # Key should be provided in the form data
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file uploaded. Ensure it is a valid type.'}), 400
    if not key:
        return jsonify({'error': 'Decryption key is required.'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)  # Save the uploaded file

    try:
        decrypted_file_path = decrypt_file(file_path, key.encode())
        return jsonify({
            'message': 'File decrypted successfully.',
            'decrypted_file_path': decrypted_file_path
        }), 200
    except Exception as e:
        return jsonify({'error': f'Decryption failed: {str(e)}'}), 500

@app.route('/upload/<provider>', methods=['POST'])
def upload_to_cloud(provider):
    """Handle file uploads to the specified cloud provider."""
    if provider not in ['gcp', 'aws']:
        return jsonify({'error': 'Invalid cloud provider selected.'}), 400
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file uploaded. Ensure it is a valid type.'}), 400

    # Placeholder logic for cloud uploads
    if provider == 'aws':
        return jsonify({'message': 'AWS upload coming soon!'}), 200
    elif provider == 'gcp':
        return jsonify({'message': 'Google Cloud upload coming soon!'}), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
