# Import necessary libraries from Flask
from flask import Flask, request, jsonify
# Import database and models for Client and HealthProgram
from models import db, Client, HealthProgram

# Initialize the Flask app
app = Flask(__name__)

# Configure the app to use a SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_info_system.db'  # Database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save resources

# Initialize the database with the app
db.init_app(app)

# Route for the home page
@app.route('/')
def home():
    return "Welcome to the Health Information System!"  # Simple welcome message

# Endpoint to create a new health program
@app.route('/programs', methods=['POST'])
def create_program():
    # Get data from the request body in JSON format
    data = request.get_json()
    
    # Create a new health program with the provided name
    new_program = HealthProgram(name=data['name'])
    
    # Add the new program to the database session
    db.session.add(new_program)
    
    # Commit the changes to the database (save the new program)
    db.session.commit()
    
    # Return a success message with HTTP status 201 (Created)
    return jsonify({'message': 'Health program created successfully'}), 201

# Endpoint to register a new client
@app.route('/clients', methods=['POST'])
def register_client():
    # Get data from the request body in JSON format
    data = request.get_json()
    
    # Create a new client with the provided name and email
    new_client = Client(name=data['name'], email=data['email'])
    
    # Add the new client to the database session
    db.session.add(new_client)
    
    # Commit the changes to the database (save the new client)
    db.session.commit()
    
    # Return a success message with HTTP status 201 (Created)
    return jsonify({'message': 'Client registered successfully'}), 201

# Endpoint to enroll a client in health programs
@app.route('/enroll', methods=['POST'])
def enroll_client():
    # Get data from the request body in JSON format
    data = request.get_json()
    
    # Find the client by email (assuming email is unique)
    client = Client.query.filter_by(email=data['email']).first()
    
    # If client is not found, return an error message
    if not client:
        return jsonify({'message': 'Client not found'}), 404
    
    # Loop through the list of program names to enroll the client
    for program_name in data['programs']:
        # Find the program by name
        program = HealthProgram.query.filter_by(name=program_name).first()
        
        # If program exists and the client is not already enrolled in it, enroll the client
        if program and program not in client.programs:
            client.programs.append(program)
    
    # Commit the changes to the database (save the enrollments)
    db.session.commit()
    
    # Return a success message with HTTP status 200 (OK)
    return jsonify({'message': 'Client enrolled in programs successfully'}), 200

# Endpoint to search for clients by name or email
@app.route('/clients/search', methods=['GET'])
def search_client():
    # Get the query parameter from the URL
    query = request.args.get('query')
    
    # Search for clients where the name or email contains the query string
    clients = Client.query.filter((Client.name.contains(query)) | (Client.email.contains(query))).all()
    
    # Return the list of found clients as a JSON response
    return jsonify([{'name': client.name, 'email': client.email} for client in clients]), 200

# Endpoint to view a specific client's profile by client ID
@app.route('/clients/<int:client_id>', methods=['GET'])
def view_client_profile(client_id):
    # Get the client by ID
    client = Client.query.get(client_id)
    
    # If the client is not found, return an error message
    if not client:
        return jsonify({'message': 'Client not found'}), 404
    
    # Prepare the client's profile data, including the programs they are enrolled in
    client_data = {
        'name': client.name,
        'email': client.email,
        'programs': [program.name for program in client.programs]  # List of program names the client is enrolled in
    }
    
    # Return the client's profile data as a JSON response
    return jsonify(client_data), 200

# Initialize the database and start the Flask app when the script is run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables if they do not exist
    app.run(debug=True)  # Run the Flask app in debug mode for development
