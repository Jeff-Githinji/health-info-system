# health-info-system
# Health Information System

A web application for managing clients and health programs, built with Flask (Python backend) and vanilla JavaScript frontend.

## Features
- Create/delete health programs (TB, Malaria, HIV, etc.)
- Register/delete clients
- Enroll clients in multiple programs
- Real-time client search
- Responsive UI with loading states

## Technologies
- **Backend**: Python, Flask, SQLAlchemy, Flask-CORS
- **Frontend**: Vanilla JS, Bootstrap 5, Font Awesome
- **Database**: SQLite (production-ready databases supported)

## Setup Instructions

### 1. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

2. Frontend Setup
# Serve the frontend (from frontend directory)
python -m http.server 8000
Access the app at: http://localhost:8000

API Endpoints
Endpoint	Method	Description
/api/programs	GET	List all programs
/api/programs	POST	Create new program
/api/programs/<id>	DELETE	Delete a program
/api/clients	GET	List all clients
/api/clients	POST	Register new client
/api/clients/<id>	DELETE	Delete a client
/api/clients/search	GET	Search clients

3. Configuration
Create .env file:
inside it, should contain:
API_KEYS=your-secret-key-123
DATABASE_URL=sqlite:///health_info.db