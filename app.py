from flask import Flask, render_template, redirect, url_for, request
from extensions import mongo
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import bcrypt
import base64


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://admin:Password123@appointmentscheduler.ikvbn6u.mongodb.net/mydb?retryWrites=true&w=majority'
# Database location on Atlas
mongo.init_app(app)



def get_hashed_password(password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)    
    # converting password to array of bytes
    bytes = password.encode('utf-8')
    # generating the salt
    salt = bcrypt.gensalt()
    # Hashing the password
    return bcrypt.hashpw(bytes, salt)


def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
      # Taking user entered password 
    
    # checking password
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)


@app.route("/login", methods =['POST', 'GET'])
def login():
    if request.method == 'POST':

        user_collection = mongo.db.Users
        username = request.form.get('username')
        pw = request.form.get('password')
        user = user_collection.find_one({'username': username})

        if user is None:
            # User not found in database
            return render_template('/login.html')
        else:
            user = user_collection.find_one({'username': username}, {'password': 1})
            password_b64 = user['password']
            
            if check_password(pw, password_b64):
                return render_template("/index.html", username = username)
            else:
                return render_template('/login.html')
    else:
        return render_template('/login.html')

@app.route("/register")
def register():
    return render_template('/register.html')

@app.route("/")
def init():
    return redirect(url_for('login'))




# https://www.mongodb.com/docs/manual/tutorial/unique-constraints-on-arbitrary-fields/

@app.route("/add_user", methods =['POST'])
def add_user():
    user_collection = mongo.db.Users
    # Table to add to
    user_name = request.form.get('username')
    email = request.form.get('email')
    name = request.form.get('name')
    pw = request.form.get('password')
    hashed_pw = get_hashed_password(pw)
    user_collection.insert_one({'name' : name, 'email': email, 'username': user_name,  'password' : hashed_pw})
    # get name from html input form
    # add name into table
    return redirect(url_for('login'))

@app.route("/setSchedule/<id>")
def setSchedule(id):
    appointment_collection = mongo.db.Appointments
    appointmentItem = request.form.get('add-appointment')
    appointment_collection.insert_one({'text' : appointmentItem})
    return redirect(url_for('home'))


@app.route("/delete_user/<id>")
def delete_user(id):
    print(id)
    user_collection = mongo.db.Users
    my_query = {'_id' : ObjectId(id)}
    user_collection.delete_one(my_query)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)