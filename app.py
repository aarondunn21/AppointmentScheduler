from flask import Flask, render_template, redirect, url_for, request,jsonify, make_response
from helpers import *
from bson.objectid import ObjectId
import datetime
from datetime import date
from datetime import timedelta

import uuid
 

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://admin:Password123@appointmentscheduler.ikvbn6u.mongodb.net/mydb?retryWrites=true&w=majority'
# Database location on Atlas
mongo.init_app(app)



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

@app.route('/profile/<id>', methods =['GET'])
def profile(id):
    if request.method == 'GET':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        id = user['public_id']
        if user is None:
            return redirect(url_for('login'), errorMsg = 'User not found')
        else:
            return render_template('/profile.html', user = user, id = id)



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
            if user['role'] == 'provider':
                # return render_template('/providerHome.html', user = user)
                return redirect(url_for('providerHome', id = user['public_id']))
            if user['role'] == 'user':
                return redirect(url_for('userHome', id = user['public_id']))
                # return render_template('/userHome.html', user = user)
            
@app.route("/providerHome/<id>",methods =['GET'])
def providerHome(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    appointment_collection = mongo.db.Appointments
    myquery =  { 'provider_name' : user['name']}
    all_appointments = appointment_collection.find(myquery)
    if request.method == 'GET':
        return render_template('/providerHome.html', user = user, appointments = all_appointments)
    else:
        try:
            
            return redirect(url_for('home',id = id))
        except Exception as e:
            return "Error in query operation "+ str(e)

@app.route("/userHome/<id>",methods =['GET'])
def userHome(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    appointment_collection = mongo.db.Appointments
    myquery =  { 'customer_name' : user['name']}
    all_appointments = appointment_collection.find(myquery)
    if request.method == 'GET':

        return render_template('/userHome.html', user = user, appointments = all_appointments)
    else:
        try:
            return redirect(url_for('home',id = id))
        except Exception as e:
            return "Error in query operation "+ str(e)

            
            



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


@app.route("/setSchedule/<id>",methods =['POST', 'GET'])
def setSchedule(id):
    if request.method == 'GET':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        if user['role'] == "user":
            return redirect(url_for('createAppointment', id = id))
        return render_template('/setSchedule.html', id = id, user = user)
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

@app.route("/createAppointment/<id>",methods =['POST', 'GET'])
def createAppointment(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    appointment_collection = mongo.db.Appointments
    myquery =  { 'customer_name' : ""}
    all_appointments = appointment_collection.find(myquery)
    if request.method == 'GET':
        return render_template('/createAppointment.html', id = id, appointments = all_appointments, user = user)
    else:
        try:
            return redirect(url_for('home',id = id))
        except Exception as e:
            return "Error in query operation "+ str(e)
        
@app.route("/addAppointment/")
def addAppointment():
    appId = request.args.get('appId')
    user_id = request.args.get('user_id')
    appointment_collection = mongo.db.Appointments
    user_collection = mongo.db.Users
    user_query = { 'public_id' : user_id}
    user = user_collection.find_one(user_query)
    myquery =  { '_id' : ObjectId(appId)}
    set_appointment = { "$set": {'customer_name' : user['name']}}
    appointment_collection.update_one(myquery, set_appointment)
    return redirect(url_for('home', id = user_id))


@app.route("/deleteAppointment/<id>/<appointmentid>", methods =['POST', 'GET'])
def deleteAppointment(id, appointmentid):
    user_query = { 'public_id' : id}
    user_collection = mongo.db.Users
    user = user_collection.find_one(user_query)
    appointment_collection = mongo.db.Appointments
    myquery =  { '_id' : ObjectId(appointmentid)}
    if user['role'] == 'provider':
        appointment_collection.delete_one(myquery)
        return redirect(url_for('providerHome', id = id))
    else:
        set_appointment = { "$set": {'customer_name' : ''}}
        appointment_collection.update_one(myquery, set_appointment)
        return redirect(url_for('userHome', id = id))


@app.route("/delete_user/<id>")
def delete_user(id):
    print(id)
    user_collection = mongo.db.Users
    my_query = {'_id' : ObjectId(id)}
    user_collection.delete_one(my_query)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)