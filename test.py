from flask import Flask, jsonify, request
import mysql.connector

# Initialize Flask app
app = Flask(__name__)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",    # Change to your MySQL server host if needed
        user="root",         # Your MySQL username
        password="ayush",  # Your MySQL password
        database="dandd"  # Your MySQL database name
    )

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Flask MySQL Connection Successful!"})

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')  # Replace 'users' with your actual table name
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(users)

# Route to add a user
@app.route('/add_user', methods=['POST'])
def add_user():
    new_user = request.json  # Assuming JSON data is sent in the request
    name = new_user['name']
    email = new_user['email']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (name, email))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "User added successfully!"}), 201

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
