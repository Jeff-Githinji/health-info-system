from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()

app = Flask(__name__)

# Enhanced CORS Configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000"],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-KEY"],
        "supports_credentials": True
    }
})

# Rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.environ.get('REDIS_URL', 'memory://'),
    default_limits=["200 per day", "50 per hour"]
)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///health_info.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['API_KEYS'] = os.environ.get('API_KEYS', '').split(',')

db = SQLAlchemy(app)

# Models
class HealthProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    programs = db.relationship('HealthProgram', secondary='client_program')

client_program = db.Table('client_program',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id')),
    db.Column('program_id', db.Integer, db.ForeignKey('health_program.id'))
)

# Decorators
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key not in app.config['API_KEYS']:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

# Routes
@app.route('/api/programs', methods=['GET', 'POST'])
@require_api_key
def handle_programs():
    if request.method == 'POST':
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
        programs = HealthProgram.query.all()
        return jsonify([{"id": p.id, "name": p.name} for p in programs])

@app.route('/api/programs/<int:program_id>', methods=['DELETE'])
@require_api_key
def delete_program(program_id):
    program = HealthProgram.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    return jsonify({"message": "Program deleted"}), 200

@app.route('/api/clients', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@require_api_key
def handle_clients():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('name') or not data.get('email'):
            return jsonify({"error": "Name and email are required"}), 400

        if Client.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Client already exists"}), 409

        client = Client(name=data['name'], email=data['email'])
        
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
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted"}), 200

@app.route('/api/clients/search', methods=['GET'])
@require_api_key
def search_clients():
    query = request.args.get('query', '')
    clients = Client.query.filter(Client.name.ilike(f'%{query}%')).all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "programs": [{"id": p.id, "name": p.name} for p in c.programs]
    } for c in clients])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)