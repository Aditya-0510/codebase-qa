from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    """
    API routing works by mapping HTTP GET requests on the /api/v1/users endpoint 
    to this get_users function in the central routing file.
    """
    return jsonify({"users": ["Alice", "Bob"]})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(port=5000)
