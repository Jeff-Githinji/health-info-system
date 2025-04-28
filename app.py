"""
Health Information System Backend
Flask API for managing health programs and patient records
"""

# ======================
# 1. SETUP AND CONFIG
# ======================
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from functools import wraps
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (Cross-Origin Resource Sharing)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000"],  # Frontend URL
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type", "X-API-KEY"]
    }
})

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day", "50 per hour"]
)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///health_info.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['API_KEYS'] = os.getenv('API_KEYS', '').split(',')  # Multiple keys supported

db = SQLAlchemy(app)

# ======================
# 2. DATABASE MODELS
# ======================
class HealthProgram(db.Model):
    """Represents a health program (e.g., TB, Malaria)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Client(db.Model):
    """Represents a patient/client"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    programs = db.relationship('HealthProgram', secondary='client_program')

# Association table for many-to-many relationship
client_program = db.Table('client_program',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),
    db.Column('program_id', db.Integer, db.ForeignKey('health_program.id'), primary_key=True)
)

# ======================
# 3. HELPER FUNCTIONS
# ======================
def require_api_key(func):
    """Decorator to validate API key in headers"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key not in app.config['API_KEYS']:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

# ======================
# 4. API ENDPOINTS
# ======================
@app.route('/api/programs', methods=['GET', 'POST'])
@require_api_key
def handle_programs():
    """Endpoint for creating and listing programs"""
    if request.method == 'POST':
        # Create new program
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"error": "Program name required"}), 400
        
        if HealthProgram.query.filter_by(name=data['name']).first():
            return jsonify({"error": "Program already exists"}), 409
            
        program = HealthProgram(name=data['name'])
        db.session.add(program)
        db.session.commit()
        return jsonify({"id": program.id, "name": program.name}), 201
    else:
        # List all programs
        programs = HealthProgram.query.all()
        return jsonify([{"id": p.id, "name": p.name} for p in programs])

@app.route('/api/programs/<int:program_id>', methods=['DELETE'])
@require_api_key
def delete_program(program_id):
    """Endpoint for deleting a program"""
    program = HealthProgram.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    return jsonify({"message": "Program deleted"}), 200

@app.route('/api/clients', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@require_api_key
def handle_clients():
    """Endpoint for creating and listing clients"""
    if request.method == 'POST':
        # Register new client
        data = request.get_json()
        if not data or not data.get('name') or not data.get('email'):
            return jsonify({"error": "Name and email are required"}), 400

        if Client.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Client already exists"}), 409

        client = Client(name=data['name'], email=data['email'])
        
        # Enroll in programs
        program_ids = data.get('programs', [])
        for pid in program_ids:
            program = HealthProgram.query.get(pid)
            if program:
                client.programs.append(program)
        
        db.session.add(client)
        db.session.commit()
        return jsonify({
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "programs": [{"id": p.id, "name": p.name} for p in client.programs]
        }), 201
    else:
        # List all clients
        clients = Client.query.all()
        return jsonify([{
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "programs": [{"id": p.id, "name": p.name} for p in c.programs]
        } for c in clients])

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
@require_api_key
def delete_client(client_id):
    """Endpoint for deleting a client"""
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted"}), 200

@app.route('/api/clients/search', methods=['GET'])
@require_api_key
def search_clients():
    """Endpoint for searching clients by name"""
    query = request.args.get('query', '')
    clients = Client.query.filter(Client.name.ilike(f'%{query}%')).all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "programs": [{"id": p.id, "name": p.name} for p in c.programs]
    } for c in clients])

# ======================
# 5. START APPLICATION
# ======================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host='0.0.0.0', port=5000, debug=True)