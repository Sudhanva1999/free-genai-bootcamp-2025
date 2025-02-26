from flask import Flask, jsonify, request
from flask_cors import CORS

from models.database import Database
from services.group_service import GroupService
from config import DEBUG

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
db = Database()
group_service = GroupService()

# Ensure database is initialized
db.initialize_db()

@app.route('/api/groups/words/<int:group_id>', methods=['GET'])
def get_words_by_id(group_id):
    """
    Get words for a specific group ID.
    Checks the database first, then falls back to LLM if no words exist.
    """
    response, status_code = group_service.get_words_by_group_id(group_id)
    return jsonify(response), status_code

@app.route('/api/groups/words/<string:group_name>', methods=['GET'])
def get_words_by_name(group_name):
    """
    Get words for a specific group name.
    Always calls the LLM and then stores the results in the database.
    """
    # Skip this function if the parameter is actually an integer (to avoid conflicts)
    if group_name.isdigit():
        return jsonify({"error": "Use numeric ID endpoint for numeric IDs"}), 400
    
    response, status_code = group_service.get_words_by_group_name(group_name)
    return jsonify(response), status_code

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5002)