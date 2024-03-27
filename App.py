from flask import Flask, jsonify, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
import datetime

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection URI
uri = "mongodb+srv://romocromo90:SsphxApuBAlkdhFc@cluster0.atmpzxm.mongodb.net/company_management_system?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Access the database and collections
db = client.company_management_system
employees_collection = db.employees

# Route to insert a sample employee data
@app.route('/insert_sample_employee', methods=['GET'])
def insert_sample_employee():
    data = {
        'name': 'Nikshep',
        'manager_name': 'John Doe',
        'last_project_name': 'Project A',
        'present_project_name': 'Project B',
        'leaves_taken': 3,
        'salary': 60000,
        'bank_account': '1234567890'
    }
    result = employees_collection.insert_one(data)
    if result.inserted_id:
        return 'Sample employee data inserted successfully'
    else:
        return 'Failed to insert sample employee data'


# Route to handle login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_name = request.form.get('employee_name')
        present_project = request.form.get('present_project')
        
        # Validate employee name and present project
        employee = employees_collection.find_one({'name': employee_name, 'present_project_name': present_project})
        if employee:
            # Redirect to the home page upon successful login
            return redirect(url_for('home'))
        else:
            # Redirect back to the login page with error message
            return render_template('login.html', error="Invalid details. Please try again.")

    # Render the login page template
    return render_template('login.html', error=None)

# Route to handle the home page
@app.route('/home')
def home():
    # Render the home page template
    return render_template('home.html')

# Route to fetch all employees
# Route to fetch all employees with their leave status
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = list(employees_collection.find({}, {'_id': False}))

    # Determine leave status for each employee
    for employee in employees:
        if employee['leaves_taken'] > 5:
            employee['leave_status'] = 'Rejected'
        else:
            employee['leave_status'] = 'Approved'

    return jsonify(employees)

# Route to search employees by name
@app.route('/employees/search', methods=['GET'])
def search_employee():
    name = request.args.get('name')
    employee = employees_collection.find_one({'name': name}, {'_id': False})
    if employee:
        return jsonify(employee)
    else:
        return jsonify({'message': 'Employee not found'}), 404

# Route to handle the form submission for adding a new employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = {
        'name': request.form['name'],
        'manager_name': request.form['manager_name'],
        'last_project_name': request.form['last_project_name'],
        'present_project_name': request.form['present_project_name'],
        'leaves_taken': int(request.form['leaves_taken']),
        'salary': int(request.form['salary']),
        'bank_account': request.form['bank_account']
    }
    result = employees_collection.insert_one(data)
    if result.inserted_id:
        # Redirect to the home page after successfully adding an employee
        return redirect(url_for('home'))
    else:
        return jsonify({'error': 'Failed to add employee'}), 500

# Route to delete an employee by name
@app.route('/employees/delete', methods=['POST'])
def delete_employee():
    # Get the employee name from the request
    employee_name = request.form.get('employee_name')

    # Attempt to delete the employee from the database
    result = employees_collection.delete_one({'name': employee_name})
    
    if result.deleted_count == 1:
        return redirect(url_for('home'))  # Redirect to home page after successful deletion
    else:
        return jsonify({'error': f'Employee "{employee_name}" not found'}), 404

# Route to update employee details by name
@app.route('/employees/update', methods=['POST'])
def update_employee():
    # Get employee details from the request
    employee_name = request.form.get('employee_name')
    new_details = {
        'manager_name': request.form.get('manager_name'),
        'last_project_name': request.form.get('last_project_name'),
        'present_project_name': request.form.get('present_project_name'),
        'leaves_taken': int(request.form.get('leaves_taken')),
        'salary': int(request.form.get('salary')),
        'bank_account': request.form.get('bank_account')
    }

    # Update the employee details in the database
    result = employees_collection.update_one({'name': employee_name}, {'$set': new_details})

    if result.modified_count == 1:
        return redirect(url_for('home'))  # Redirect to home page after successful update
    else:
        return jsonify({'error': f'Employee "{employee_name}" not found'}), 404

# Route to render the add employee page
@app.route('/add_employee')
def render_add_employee_page():
    return render_template('add_employee.html')


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
