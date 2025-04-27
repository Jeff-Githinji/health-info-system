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

@app.route('/enroll', methods=['POST'])
def enroll_client():
    data = request.get_json()
    client = Client.query.filter_by(email=data['email']).first()
    if not client:
        return jsonify({'message': 'Client not found'}), 404

    for program_name in data['programs']:
        program = HealthProgram.query.filter_by(name=program_name).first()
        if program and program not in client.programs:
            client.programs.append(program)

    db.session.commit()
    return jsonify({'message': 'Client enrolled in programs successfully'}), 200

@app.route('/clients/search', methods=['GET'])
def search_client():
    query = request.args.get('query')
    clients = Client.query.filter((Client.name.contains(query)) | (Client.email.contains(query))).all()
    return jsonify([{'name': client.name, 'email': client.email} for client in clients]), 200

@app.route('/clients/<int:client_id>', methods=['GET'])
def view_client_profile(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'message': 'Client not found'}), 404

    client_data = {
        'name': client.name,
        'email': client.email,
        'programs': [program.name for program in client.programs]
    }
    return jsonify(client_data), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)