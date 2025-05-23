import psycopg2
from generate_firebase_config import generate_config_file
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from waitress import serve
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.utils import cloudinary_url
import base64
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth as firebase_auth
from model import load_model, predict
from database.db_config import get_connection
import cloudinary_config
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import smtplib
import random
from email.message import EmailMessage
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.DEBUG)


load_dotenv()

EMAIL_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PASS = os.getenv("EMAIL_HOST_PASSWORD")
otp_store = {}

generate_config_file()

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result or not result[0]:
            return jsonify({"error": "Admin access required"}), 403

        return f(*args, **kwargs)
    return decorated


app = Flask(__name__, static_folder=os.path.abspath("../frontend/dist"), static_url_path="/")
app.config.update(
    SESSION_COOKIE_SAMESITE="None",  # allow cross-site cookies
    SESSION_COOKIE_SECURE=True,       # only send over HTTPS
)


CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://stego-shield.vercel.app",
    "https://stegoshield-3ius.onrender.com"
])



app.secret_key = "your-secret-key"  # Replace with a strong secret key

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# Load model once at startup
#model = load_model()

@app.route("/ping", methods=["GET"])
def ping():
    return {"status": "ok", "message": "StegoShield backend is alive 🎯"}, 200


# --------------------- DATABASE TEST ROUTE ---------------------

@app.route("/api/test_db", methods=["GET"])
def test_db():
    try:
        print("Testing database connection...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uploads LIMIT 5;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": rows})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    new_password = data.get('password')  # New password (optional)
    old_password = data.get('oldPassword')  # Optional
    avatar = data.get('avatar')      # base64 string
    theme = data.get('theme')

    avatar_url = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch current password hash from DB
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "User not found"}), 404

        current_hashed_password = result[0]

        # If user is trying to update password, verify old password
        hashed_new_password = None
        if new_password:
            if not old_password:
                return jsonify({"message": "Old password is required to update password"}), 400

            if not check_password_hash(current_hashed_password, old_password):
                return jsonify({"message": "Incorrect current password"}), 403

            hashed_new_password = generate_password_hash(new_password)

        if avatar and avatar.startswith("data:image"):
            # Extract base64 from Data URL
            base64_data = re.sub('^data:image/.+;base64,', '', avatar)
            decoded_img = base64.b64decode(base64_data)

            # Upload to Cloudinary
            result = cloudinary_upload(decoded_img, folder="avatars", public_id=f"user_{user_id}", overwrite=True)
            avatar_url = result.get("secure_url")


        query = """
            UPDATE users 
            SET 
                name = %s,
                email = %s,
                password = COALESCE(%s, password),
                avatar = COALESCE(%s, avatar),
                theme = %s
            WHERE id = %s
            RETURNING id, name, email, avatar, theme, is_admin, created_at, auth_provider;
        """

        cursor.execute(query, (
            name,
            email,
            hashed_new_password,
            avatar_url,
            theme,
            user_id
        ))

        updated_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not updated_user:
            return jsonify({"message": "User not found"}), 404

        user_data = {
            "id": updated_user[0],
            "name": updated_user[1],
            "email": updated_user[2],
            "avatar": updated_user[3],
            "theme": updated_user[4],
            "is_admin": updated_user[5],
            "created_at": updated_user[6],
            "auth_provider": updated_user[7],
        }

        return jsonify(user_data)

    except Exception as e:
        print("Error updating user:", e)
        return jsonify({"error": str(e)}), 500

# --------------------- SERVE REACT FRONTEND ---------------------

@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

# --------------------- AUTH ROUTES ---------------------

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    hashed_pw = generate_password_hash(password)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password, auth_provider) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_pw, 'email')
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Signup successful!"})
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Email already registered"}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    
@app.route("/api/update-password", methods=["POST"])
def update_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("newPassword")
    
    if not email or not new_password:
        return jsonify({"success": False, "message": "Email and new password are required"}), 400
    
    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Update password in database
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s RETURNING id, name, email",
            (hashed_password, email)
        )
        updated_user = cursor.fetchone()
        conn.commit()
        
        if updated_user:
            user_id, name, email = updated_user
            return jsonify({
                "success": True,
                "message": "Password updated successfully",
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email
                }
            })
        else:
            return jsonify({"success": False, "message": "Failed to update password"}), 500
            
    except Exception as e:
        conn.rollback()
        print(f"Error updating password: {e}")
        return jsonify({"success": False, "message": "Error updating password"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route("/google-signup", methods=["POST"])
def google_signup():
    data = request.get_json()
    name = data.get("name")
    print(name)
    email = data.get("email")
    print(email)

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            user_id, name = existing_user
        else:
            # New user signup (no password needed for Google auth)
            cursor.execute(
                "INSERT INTO users (name, email, auth_provider) VALUES (%s, %s, %s) RETURNING id",
                (name, email, 'google')
            )
            user_id = cursor.fetchone()[0]
            conn.commit()

        cursor.close()
        conn.close()
        return jsonify({
            "message": "Google signup/login successful",
            "user": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }), 200

    except Exception as e:
        conn.rollback()
        print(f"Google signup error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST" , "OPTIONS"])
def login():
    print("🔥 Login route called", flush=True)
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        print("sneha options")
        return response, 204 
    data = request.get_json()
    print(data)
    email = data.get("email")
    password = data.get("password")

    try:
        conn = get_connection()
        cursor = conn.cursor()



        # Fetch name AND avatar along with password
        cursor.execute("SELECT id, name, password, avatar FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user is None:
            return jsonify({"message": "User not found"}), 404

        user_id, name, hashed_password, avatar = user

        if not hashed_password or not isinstance(hashed_password, str):
            return jsonify({"message": "Invalid Credentials"}), 500

        if not check_password_hash(hashed_password, password):
            return jsonify({"message": "Incorrect passworddd"}), 401

        session['user_id'] = user_id
        print(session['user_id'])

        # ✅ Create response and manually set CORS headers
        response = jsonify({
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "avatar": avatar
            }
        })
        # Set the origin header to match the request origin
        allowed_origins = [
            "http://localhost:5173",
            "https://stego-shield.vercel.app",
            "https://stegoshield-3ius.onrender.com"
        ]
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"message": "Server error", "error": str(e)}), 500

@app.route("/google-login", methods=["POST"])
def google_login():
    try:
        data = request.get_json()
        id_token = data.get("idToken")

        # Verify the token with Firebase Admin SDK
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get("email")
        uid = decoded_token.get("uid")
        name = decoded_token.get("name")
        avatar = decoded_token.get("picture")  # 🎯 This is the profile picture URL

        # Connect to your DB and check if user exists
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, avatar FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            # New user – insert into DB with name and avatar
            cursor.execute(
                """
                INSERT INTO users (name, email, google_uid, auth_provider, avatar)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (name, email, uid, 'google', avatar)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
        else:
            user_id, name, avatar = user  # Also pull avatar from DB

        cursor.close()
        conn.close()

        session['user_id'] = user_id
        print("Session after login:", dict(session))
        return jsonify({
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "avatar": avatar  # Send back the profile pic
            }
        }), 200

    except Exception as e:
        print(f"Google login error: {e}")
        return jsonify({"message": "Google login failed", "error": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"})

# --------------------- PREDICTION ROUTE ---------------------

@app.route('/upload', methods=['POST', 'GET' , 'OPTIONS'])
def detect():
    if request.method == "OPTIONS":
        return '', 204 
    if request.method == 'GET':
        return "StegoShield API is running! Use POST request to analyze files."

    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filetype = filename.rsplit('.', 1)[-1].lower()
    
    # Get file size from the uploaded file
    file_size = request.content_length  # This gets the size in bytes
    if file_size is None:
        # Fallback method if content_length isn't available
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

    print(f"DEBUG: Uploading {filename} (Type: {filetype}, Size: {file_size} bytes)")

    try:
        # 🔹 Upload file to Cloudinary
        cloud_result = cloudinary_upload(file, resource_type="auto")
        print("DEBUG cloud_result:", cloud_result)
        file_url = cloud_result['secure_url']

        # 🔹 Run prediction (lazy-load model only once)
        file.stream.seek(0)  # Reset stream
        if not hasattr(app, 'model'):
            from model import load_model
            app.model = load_model()  # full model dict (image, audio, video)

        result, confidence = predict(file, model=app.model)
        print("Prediction result:", result, "Confidence:", confidence)

        # 🔹 Save results to DB with file_size
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO results (filename, prediction, confidence, user_id, file_url, file_size)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (filename, result, confidence, session['user_id'], file_url, file_size))

        cursor.execute("""
            INSERT INTO uploads (filename, filetype, result, file_url, user_id, file_size)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (filename, filetype, result, file_url, session['user_id'], file_size))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "result": result,
            "confidence": confidence,
            "file_url": file_url,
            "filename": filename,
            "file_size": file_size  # Include file size in response
        })

    except Exception as e:
        print("Error in /upload:", e)
        return jsonify({"error": str(e)}), 500

    
@app.route("/api/history", methods=["GET"])
def get_user_history():
    print("hello")
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch from uploads table for dashboard history
        cursor.execute("""
            SELECT id, filename, filetype, result, file_url, created_at , file_size 
            FROM uploads 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        print(rows)

        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "result": row[3],
                "url": row[4],
                "date": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None,
                "size": row[6],
            })

        # Optionally add confidence from `results` table if needed:
        cursor.execute("""
            SELECT filename, confidence 
            FROM results 
            WHERE user_id = %s
        """, (user_id,))
        result_map = {r[0]: r[1] for r in cursor.fetchall()}

        for item in history:
            item["confidence"] = result_map.get(item["name"], 0)

        cursor.close()
        conn.close()

        return jsonify(history)

    except Exception as e:
        print("Error fetching history:", e)
        return jsonify({"error": str(e)}), 500

# Add this route anywhere with your other routes (before the error handler)
@app.route("/api/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # First verify the history item belongs to the current user
        cursor.execute("SELECT user_id FROM uploads WHERE id = %s", (history_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "History item not found"}), 404

        if result[0] != session['user_id']:
            return jsonify({"error": "Unauthorized to delete this item"}), 403

        # Get filename before deleting (to delete from results table)
        cursor.execute("SELECT filename FROM uploads WHERE id = %s", (history_id,))
        filename = cursor.fetchone()[0]

        # Delete from uploads table
        cursor.execute("DELETE FROM uploads WHERE id = %s", (history_id,))
        
        # Also delete from results table (if exists)
        cursor.execute("DELETE FROM results WHERE filename = %s AND user_id = %s", 
                      (filename, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "History item deleted successfully"})

    except Exception as e:
        print("Error deleting history:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/history/all", methods=["DELETE"])
def clear_all_history():
    data = request.get_json()
    print("Received data:", data)
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_connection()
        cursor = conn.cursor()
        user_id = session['user_id']
        print("User ID:", user_id)

        # Delete all user's uploads and get the filenames
        cursor.execute("DELETE FROM uploads WHERE user_id = %s RETURNING filename", (user_id,))
        deleted_files = cursor.fetchall()
        filenames = [file[0] for file in deleted_files]

        # Delete matching results
        if filenames:
            cursor.execute(
                "DELETE FROM results WHERE user_id = %s AND filename = ANY(%s)",
                (user_id, filenames)
            )

        conn.commit()
        return jsonify({
            "message": "All history cleared successfully",
            "deleted_count": len(filenames)
        })

    except Exception as e:
        conn.rollback()
        print("Error clearing history:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# --------------------- PASSWORD RESET ---------------------

@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    print("Received email for OTP:", email)  # Add this

    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    otp = f"{random.randint(1000, 9999)}"
    otp_store[email] = otp
    print("Generated OTP:", otp)  # Add this

    try:
        msg = EmailMessage()
        msg["Subject"] = "Your OTP for Password Reset"
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg.set_content(f"Your OTP code is: {otp}")

        print("Trying to send email...")  # Add this

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("OTP sent successfully!")  # Add this
        return jsonify({"success": True, "message": "OTP sent successfully"})

    except Exception as e:
        print("Error sending OTP:", e)  # 👈 This will show the actual error
        return jsonify({"success": False, "message": "Failed to send OTP"}), 500

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp_input = data.get("otp")

    real_otp = otp_store.get(email)

    if real_otp and otp_input == real_otp:
        token = f"{random.randint(100000, 999999)}"  # In production, use JWT
        session[f"reset_token_{email}"] = token
        del otp_store[email]
        return jsonify({"success": True, "token": token})

    return jsonify({"success": False, "message": "Invalid or expired OTP"}), 400

# --------------------- FRONTEND ROUTING FALLBACK ---------------------

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

# --------------------- RUN SERVER ---------------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=port)
