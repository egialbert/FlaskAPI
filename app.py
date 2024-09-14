from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api # to route incoming url
from flask_sqlalchemy import SQLAlchemy # to interract with database

# create an instance of flask
app = Flask(__name__)


# create an instance of Api for our app
# to help with url routing
api = Api(app)

# create a database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create an instance of sqlalchemy and set it to db
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()


# define a class representing an employee
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(80), nullable=False)
    salary = db.Column(db.Float)

    def __repr__(self):
        return f"{self.firstname} - {self.lastname} - {self.gender} - {self.salary}"

# for GET request to http://localhost:5000/
# API that services an incoming request
class GetEmployee(Resource):
    def get(self):
        employee = Employee.query.all() # collecting all the employee records (data) an saving them to a variable
        emp_list = [] # create a list to save the collected employee records (data) in a list
        for emp in employee: # loop through the employee data
            emp_data = {'Id':emp.id, 'FirstName':emp.firstname, 'LastName':emp.lastname, 'Gender':emp.gender,
                        'Salary':emp.salary} # mapping the the employee data in a key value pairs as in a dictionary
            emp_list.append(emp_data)
        return {"Employees":emp_list}, 200


# for POST request to http://localhost:5000/employee
class AddEmployee(Resource):
    def post(self):
        if request.is_json: # check if the sent request is json
            emp = Employee(firstname=request.json['FirstName'], lastname=request.json['LastName'], 
                           gender=request.json['Gender'], salary=request.json['Salary']) #map the employee attribute to the incoming json data
            db.session.add(emp)
            db.session.commit()
            # return the  response
            return make_response(jsonify({'Id':emp.id, 'First Name':emp.firstname, 'Last Name':emp.lastname, 'Gender':emp.gender, 'Salary':emp.salary}), 201) # return the response in a json format
        else: # if not in proper json format return an error!
            return {'error':'Request must be JSON'}, 400

            
# define a class to update existing employee record (daata)
# for PUT request to http://localhost:5000/update/?
class UpdateEmployee(Resource):
    def put(self, id):
        if request.is_json: # check if the sent request is json
            emp = Employee.query.get(id) # query the database with the incoming id
            if emp is None: # if the employee does not exist
                return {'error': 'not found'}, 404
            else: # map the employee attribute with the incoming data from the request
                emp.firstname = request.json['FirstName']
                emp.lastname = request.json['LastName']
                emp.gender = request.json['Gender']
                emp.salary = request.json['Salary']
                db.session.commit()
                return 'Updated', 200
        else:
            return {'error':'Request must be JSON'}, 404

# define a class to delete existing employee record (daata)
# for PUT request to http://localhost:5000/delete/?
class DeleteEmployee(Resource):
    def delete(self, id):
        emp = Employee.query.get(id) # query the database with the incoming id
        if emp is None: # if the employee does not exist
            return{'error':'not found'}, 400
        db.session.delete(emp)
        db.session.commit()
        return f'{id} is deleted', 200
    
# register the route (add_resource), so the API will know how to route a request to a particular class
api.add_resource(GetEmployee, '/')
api.add_resource(AddEmployee, '/add')
api.add_resource(UpdateEmployee, '/update/<int:id>')
api.add_resource(DeleteEmployee, '/delete/<int:id>')

if __name__ == '__name__':
    app.run(debug=True)