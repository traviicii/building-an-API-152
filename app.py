from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connection, Error

app = Flask(__name__)
ma = Marshmallow(app)

# Create the Customer table schema, to define the structure of our data that we expect to send and recieve
class CustomerSchema(ma.Schema):
    id = fields.Int(dump_only= True) # dump_only means we don't have to input data for this field
    customer_name = fields.String(required= True) # to be valid, this needs a value
    email = fields.String()
    phone = fields.String()

    class Meta:
        fields = ("id", "customer_name", "email", "phone")

customer_schema = CustomerSchema() # allows us to validate data for single customers when we send and recieve
customers_schema = CustomerSchema(many = True) # allow us to validate multiple rows or entries from our customer table at the same time


@app.route('/') # Default landing page - always need to include a '/' route in your API or website
def home():
    return "Hello, Flask!"

@app.route('/cool') # blahblah.com/cool
def cool():
    return "Welcome to the extravaganzaaaaaa!!!!"

# @app.route('/pokemon/<str:pokename>') # might be incorrect syntax, but this is a general example
# def pokedex(pokename):
    # some code to get the specific pokemon from our database

#--------------------

# CRUD Operations
# Create (POST)
# Retrieve (GET)
# Update (PUT)
# Delete (DELETE)

# route to GET all customers
@app.route('/customers', methods = ['GET'])
def get_customers():
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True) # returns us a dictionary of table data instead of a tuple, our schema meta class will cross check the contents of the dictionaries that are returned to us

            # write our query to GET all customers
            query = "SELECT * FROM customer;"

            cursor.execute(query)

            customers = cursor.fetchall()

        except Error as e:
            print(f"Error: {e}")
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return customers_schema.jsonify(customers)


# Create a new customer with a POST request
@app.route("/customers", methods = ['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            #new customer data
            new_customer = (customer_data['customer_name'], customer_data['email'], customer_data['phone'])

            # query
            query = "INSERT INTO customer (customer_name, email, phone) VALUES (%s, %s, %s)"

            # excecute the query with new_customer data
            cursor.execute(query, new_customer)
            conn.commit()

            return jsonify({'message': 'New customer added successfully!'}), 201
        
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'error': 'Database connection failed'}), 500

@app.route("/customers/<int:id>", methods = ['PUT']) # dynamic route that can change based off of different query parameters
def update_customer(id):
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Query to check if we even have this customer in our database
            check_query = "SELECT * FROM customer WHERE id = %s;"
            cursor.execute(check_query, (id,))
            customer = cursor.fetchone()
            if not customer:
                return jsonify({"error": "Customer was not found."}), 404
            
            # create updated customer info tuple
            updated_customer = (customer_data['customer_name'], customer_data['email'], customer_data['phone'], id)

            query = "UPDATE customer SET customer_name = %s, email = %s, phone = %s WHERE id = %s;"
            cursor.execute(query, updated_customer)
            conn.commit()

            return jsonify({'message': f"Successfully updated customer {id}"}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500


@app.route("/customers/<int:id>", methods = ['DELETE'])
def delete_customer(id):

    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM customer WHERE id = %s;"
            cursor.execute(check_query, (id,))
            customer = cursor.fetchone()
            if not customer:
                return jsonify({"error": "Customer was not found"}), 404
            
            query = "DELETE FROM customer WHERE id = %s;"
            cursor.execute(query, (id,))
            conn.commit()

            return jsonify({"message": f"Customer {id} was successfully destroyed!"})
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()

    else:
        return jsonify({"error": "Database connection failed"}), 500


if __name__ == '__main__':
    app.run(debug= True)