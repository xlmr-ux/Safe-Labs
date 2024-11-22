from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import os
import sqlite3
import logging
from werkzeug.utils import secure_filename

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

app = Flask(__name__)

# Load or generate encryption key
SECRET_KEY = os.getenv('ENCRYPTION_KEY')
if not SECRET_KEY:
    logging.warning("ENCRYPTION_KEY environment variable not set, generating a new key.")
    SECRET_KEY = Fernet.generate_key()
    with open(".encryption_key", "wb") as key_file:
        key_file.write(SECRET_KEY)

cipher = Fernet(SECRET_KEY)

# File upload directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
DATABASE_FILE = 'file_data.db'

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    logging.debug("Database initialized.")

# Initialize the database
init_db()

# File validation
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler for consistent error responses."""
    logging.error(f"Unexpected error: {e}")
    return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    """Encrypt a file and save the encrypted file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filename = secure_filename(file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_path)
        logging.debug(f"File saved: {original_path}")

        # Encrypt file
        with open(original_path, 'rb') as f:
            encrypted_data = cipher.encrypt(f.read())

        encrypted_path = f"{original_path}.enc"
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        logging.debug(f"File encrypted: {encrypted_path}")

        return jsonify({"message": "File encrypted successfully", "path": encrypted_path})
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        return jsonify({"error": "Encryption failed", "details": str(e)}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    """Decrypt an encrypted file and save the original file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        filename = secure_filename(file.filename)
        encrypted_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(encrypted_path)
        logging.debug(f"Encrypted file saved: {encrypted_path}")

        # Decrypt file
        with open(encrypted_path, 'rb') as f:
            decrypted_data = cipher.decrypt(f.read())

        decrypted_path = encrypted_path.replace('.enc', '')
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        logging.debug(f"File decrypted: {decrypted_path}")

        return jsonify({"message": "File decrypted successfully", "path": decrypted_path})
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        return jsonify({"error": "Decryption failed", "details": str(e)}), 500

@app.route('/upload/database', methods=['POST'])
def upload_to_database():
    """Upload a file to the database."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        logging.debug(f"File saved for database upload: {file_path}")

        # Insert file details into the database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (filename, file_path) VALUES (?, ?)", (filename, file_path))
        conn.commit()
        conn.close()
        logging.debug(f"File inserted into database: {filename}")

        return jsonify({"message": f"File uploaded and saved in the database: {filename}"})
    except sqlite3.Error as db_error:
        logging.error(f"Database error: {db_error}")
        return jsonify({"error": "Database error", "details": str(db_error)}), 500

@app.route('/list/files', methods=['GET'])
def list_files():
    """List all files stored in the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename FROM files")
        files = cursor.fetchall()
        conn.close()
        logging.debug(f"Files fetched: {files}")

        return jsonify({"files": [{"id": file[0], "filename": file[1]} for file in files]})
    except Exception as e:
        logging.error(f"Failed to fetch file details: {e}")
        return jsonify({"error": "Failed to fetch file details", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
