from flask import Flask, request, jsonify
from models import db, Client, HealthProgram

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_info_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return "Welcome to the Health Information System!"

@app.route('/programs', methods=['POST'])
def create_program():
    data = request.get_json()
    new_program = HealthProgram(name=data['name'])
    db.session.add(new_program)
    db.session.commit()
    return jsonify({'message': 'Health program created successfully'}), 201

@app.route('/clients', methods=['POST'])
def register_client():
    data = request.get_json()
    new_client = Client(name=data['name'], email=data['email'])
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client registered successfully'}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)