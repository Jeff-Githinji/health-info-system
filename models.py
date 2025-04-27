# Import SQLAlchemy for interacting with the database
from flask_sqlalchemy import SQLAlchemy

# Initialize an instance of SQLAlchemy for the database interaction
db = SQLAlchemy()

# Define the Client model (table) for storing client information
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each client (primary key)
    name = db.Column(db.String(100), nullable=False)  # Client's name, must not be empty
    email = db.Column(db.String(100), unique=True, nullable=False)  # Client's email, must be unique and not empty
    
    # Relationship to the HealthProgram model via the 'enrollments' association table
    programs = db.relationship('HealthProgram', secondary='enrollments', back_populates='clients')

# Define the HealthProgram model (table) for storing health program information
class HealthProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each health program (primary key)
    name = db.Column(db.String(100), unique=True, nullable=False)  # Program name, must be unique and not empty
    
    # Relationship to the Client model via the 'enrollments' association table
    clients = db.relationship('Client', secondary='enrollments', back_populates='programs')

# Define the 'enrollments' association table to establish a many-to-many relationship
enrollments = db.Table('enrollments',
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'), primary_key=True),  # Foreign key to the Client model
    db.Column('program_id', db.Integer, db.ForeignKey('health_program.id'), primary_key=True)  # Foreign key to the HealthProgram model
)

