from flask import Flask, render_template, redirect, url_for, request,jsonify, make_response
from extensions import mongo
from bson.objectid import ObjectId
import datetime
from datetime import date
from datetime import timedelta
import bcrypt
import uuid
 

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
            user = user_collection.find_one({'username': username}, {'password': 1} )
            password_b64 = user['password']
            
            if check_password(pw, password_b64):
                user = user_collection.find_one({'username': username}, {'public_id': 1})
                public_id = user['public_id']
                return redirect(url_for('home', id = public_id)  )          
            else:
                # returns 403 if password is wrong
                return make_response('Could not verify',403,{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'})

    else:
        return render_template('/login.html')

@app.route("/register")
def register():
    return render_template('/register.html')

@app.route("/")
def home(methods =['GET']):
    if request.method == 'GET':
        if request.args.get('id') is None:
            return redirect(url_for('login'))
        else:
            public_id = request.args.get('id')
            user_collection = mongo.db.Users
            user = user_collection.find_one({'public_id': public_id})
            if user is None:
                return redirect(url_for('login'), errorMsg = 'User not found')
            
            return render_template('/home.html', user = user)



# https://www.mongodb.com/docs/manual/tutorial/unique-constraints-on-arbitrary-fields/

@app.route("/add_user", methods =['POST'])
def add_user():
    user_collection = mongo.db.Users
    # Table to add to
    user_name = request.form.get('username')
    email = request.form.get('email')
    name = request.form.get('name')
    pw = request.form.get('password')
    phone = request.form.get('phone')
    provider = request.form.get('provider')
    if provider:
        role = 'provider'
    else:
        role = 'user'

    hashed_pw = get_hashed_password(pw)
    user_collection.insert_one({'name' : name, 'email': email, 'phone':phone , 'username': user_name,  'password' : hashed_pw , 'role': role, "public_id": str(uuid.uuid4())})
    # get name from html input form
    # add name into table
    return redirect(url_for('login'))


def getUserEmail(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    if user == None:
        return None
    else:
        return user['email']
    
def getUsersName(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    if user == None:
        return None
    else:
        return user['name']
    
def getPhoneNumber(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    if user == None:
        return None
    else:
        return user['phone']

@app.route("/setSchedule/<id>",methods =['POST', 'GET'])
def setSchedule(id):
    if request.method == 'GET':
        return render_template('/setSchedule.html', id = id)
    else:
        appointment_collection = mongo.db.Appointments
        try:
            name = getUsersName(id)
            email = getUserEmail(id)
            phone = getPhoneNumber(id)

            # Grab the schedule data
            schedule_data = [
                ('Monday', request.form['monday_start'], request.form['monday_end']),
                ('Tuesday', request.form['tuesday_start'], request.form['tuesday_end']),
                ('Wednesday', request.form['wednesday_start'], request.form['wednesday_end']),
                ('Thursday', request.form['thursday_start'], request.form['thursday_end']),
                ('Friday', request.form['friday_start'], request.form['friday_end']),
                ('Saturday', request.form['saturday_start'], request.form['saturday_end']),
                ('Sunday', request.form['sunday_start'], request.form['sunday_end'])
            ]
                        # Define the start date and number of weeks

   
            today = datetime.datetime.today()
                
                #calculate the date of the next monday
            monday = today + timedelta(days=(7 - today.weekday()) % 7)

                # Loop through the schedule data and insert appointments for the specified number of weeks
                # Generate appointments for each week
            for i in range(int(request.form['numweeks'])):
                for day, start_time, end_time in schedule_data:
                        if start_time and end_time:
                            # Determine the date for this day of the week
                            currentdate = monday + timedelta(days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(day))
                            
                            appointment_collection.insert_one({'start_time' : currentdate.strftime('%Y-%m-%d') + ' ' + start_time, 'end_time' : currentdate.strftime('%Y-%m-%d') + ' ' + end_time, 'date' : currentdate, 'customer_name' : '', 'provider_name': name, 'location' :'N/A', 'Notes': 'N/A'})
            return redirect(url_for('home',id = id))
        except Exception as e:
            return "Error in query operation "+ str(e)


@app.route("/delete_user/<id>")
def delete_user(id):
    print(id)
    user_collection = mongo.db.Users
    my_query = {'_id' : ObjectId(id)}
    user_collection.delete_one(my_query)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)