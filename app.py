from flask import Flask, request, jsonify
import hmac
import hashlib
import urllib.parse
import json
import os
from dotenv import load_dotenv
import openai
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Post

app = Flask(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Config
DB_PARAMS = {
    "host": os.getenv('DB_HOST'),
    "database": os.getenv('DB_DATABASE'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "port": os.getenv('DB_PORT')
}

DB_URL = os.getenv('DB_URL') or f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}"

if not all([BOT_TOKEN, DB_URL]):
    raise ValueError("Missing environment variables.")

# SQLAlchemy setup
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# OpenAI setup
openai.api_key = OPENAI_API_KEY

# Verify Telegram init data
def verify_init_data(init_data_str):
    try:
        # Parse URL-encoded init_data string
        parsed_data = urllib.parse.parse_qs(init_data_str)
        if not parsed_data:
            return None

        # Create data-check-string (sorted key-value pairs, excluding hash)
        data_check_string = '\n'.join(
            f"{key}={value[0]}" for key, value in sorted(parsed_data.items()) if key != 'hash'
        )
        
        # Generate secret key using BOT_TOKEN
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Verify hash
        if calculated_hash == parsed_data.get('hash', [''])[0]:
            # Extract user ID from user field (JSON-encoded)
            user_data = json.loads(parsed_data.get('user', ['{}'])[0])
            return user_data.get('id')
        return None
    except Exception:
        return None

@app.route('/api/post/<post_id>', methods=['GET'])
def get_post_text(post_id):
    #init_data = request.headers.get('X-Telegram-Init-Data')
    #if not init_data:
    #    return jsonify({'error': 'No Telegram init data provided'}), 401
    
    #user_id = verify_init_data(init_data)
    #if not user_id:
    #    return jsonify({'error': 'Invalid Telegram init data'}), 401
    user_id = 'user_5483587510'
    
    
    # For simplicity, assume post_id is message_id and text is stored in DB
    session = Session()
    try:
        post = session.query(Post).filter_by(id=post_id, account_used=user_id).first()
        if not post:
            return jsonify({'error': 'Post not found or not authorized'}), 404
        return jsonify({'text': post.original_text or ''})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

#if __name__ == '__main__':
#    app.run(host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))