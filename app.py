from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
from helpers import *
from bson.objectid import ObjectId
import datetime
from datetime import date
from datetime import timedelta

import uuid

app = Flask(__name__)
app.config[
    'MONGO_URI'] = 'mongodb+srv://admin:Password123@appointmentscheduler.ikvbn6u.mongodb.net/mydb?retryWrites=true&w=majority'
# Database location on Atlas
mongo.init_app(app)


# Login page (base path will redirect here if user is not logged in)
@app.route("/login", methods=['POST', 'GET'])
def login():
    # if user info has been received in the form, try to sign them in
    if request.method == 'POST':

        user_collection = mongo.db.Users
        username = request.form.get('username')
        pw = request.form.get('password')
        user = user_collection.find_one({'username': username})

        # no user found by that name? go back to login
        if user is None:
            return render_template('/login.html')
        else:
            user = user_collection.find_one({'username': username}, {'password': 1})
            password_b64 = user['password']

            # if password is good, send user to appropriate homepage
            if check_password(pw, password_b64):
                user = user_collection.find_one({'username': username}, {'public_id': 1})
                public_id = user['public_id']
                return redirect(url_for('home', id=public_id))

            else:
                # error messsage if invalid password
                return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'})

    else:
        # if the form has not been filled out yet, route user to the form
        return render_template('/login.html')


# send user to registration form
@app.route("/register")
def register():
    return render_template('/register.html')


# display the user (non-provider) homepage, passing Appointments table queries to the HTML file for display
@app.route("/userHome/<id>", methods=['GET'])
def userHome(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    appointment_collection = mongo.db.Appointments

    # get past and future appointments for the user
    myquery = {'$and': [{'customer_name': user['name']},
                        {'start_time': {'$gt': datetime.datetime.now().strftime('%Y-%m-%d')}}]}
    myquery_past = {
        '$and': [{'customer_name': user['name']}, {'end_time': {'$lt': datetime.datetime.now().strftime('%Y-%m-%d')}}]}
    future_appointments = appointment_collection.find(myquery).sort("start_time", 1)
    past_appointments = appointment_collection.find(myquery_past).sort("start_time", 1)

    if request.method == 'GET':
        return render_template('/userHome.html', user=user, appointments_future=future_appointments,
                               past_appointments=past_appointments)
    else:
        try:
            return redirect(url_for('home', id=id))
        except Exception as e:
            return "Error in query operation " + str(e)


# similar to above, making appropriate queries for the provider homepage
@app.route("/providerHome/<id>", methods=['GET'])
def providerHome(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    appointment_collection = mongo.db.Appointments

    myquery = {'$and': [{'provider_name': user['name']},
                        {'start_time': {'$gt': datetime.datetime.now().strftime('%Y-%m-%d')}}]}
    future_appointments = appointment_collection.find(myquery)
    myquery_past = {
        '$and': [{'provider_name': user['name']}, {'end_time': {'$lt': datetime.datetime.now().strftime('%Y-%m-%d')}}]}
    future_appointments = appointment_collection.find(myquery).sort("start_time", 1)
    past_appointments = appointment_collection.find(myquery_past).sort("start_time", 1)

    if request.method == 'GET':
        return render_template('/providerHome.html', user=user, appointments_future=future_appointments,
                               past_appointments=past_appointments)
    else:
        try:
            return redirect(url_for('home', id=id))
        except Exception as e:
            return "Error in query operation " + str(e)


# display the user's profile page
@app.route('/profile/<id>', methods=['GET'])
def profile(id):
    if request.method == 'GET':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        id = user['public_id']

        # if no one exists with this id, send user to login
        if user is None:
            return redirect(url_for('login'), errorMsg='User not found')
        # if user is found, send along their info to the HTML page
        else:
            return render_template('/profile.html', user=user, id=id)


# route the user either to log in, or to their appropriate homepage
@app.route("/")
def home(methods=['GET']):
    if request.method == 'GET':
        if request.args.get('id') is None:
            return redirect(url_for('login'))
        else:
            public_id = request.args.get('id')
            user_collection = mongo.db.Users
            user = user_collection.find_one({'public_id': public_id})
            if user is None:
                return redirect(url_for('login'), errorMsg='User not found')
            if user['role'] == 'provider':
                return redirect(url_for('providerHome', id=user['public_id']))
            if user['role'] == 'user':
                return redirect(url_for('userHome', id=user['public_id']))


# https://www.mongodb.com/docs/manual/tutorial/unique-constraints-on-arbitrary-fields/


# takes register.html form and runs SQL to add a new user to the table
# (could this be integrated into the register function? see login for reference.
@app.route("/add_user", methods=['POST'])
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
    user_collection.insert_one(
        {'name': name, 'email': email, 'phone': phone, 'username': user_name, 'password': hashed_pw, 'role': role,
         "public_id": str(uuid.uuid4())})
    # get name from html input form
    # add name into table
    return redirect(url_for('login'))


# remove a user
@app.route("/delete_user/<id>")
def delete_user(id):
    print(id)
    user_collection = mongo.db.Users
    my_query = {'_id': ObjectId(id)}
    user_collection.delete_one(my_query)
    return redirect(url_for('home'))


# change the user's password
@app.route("/change_password/<id>", methods=['POST', 'GET'])
def change_password(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})

    # if the form hasn't been filled out, direct user to form
    if request.method == 'GET':
        return render_template('/reset.html', id=user['public_id'], username=user['username'])
    # use form info to update user
    else:
        current_pass = request.form.get('currentpassword')
        new_pass = request.form.get('newpassword')

        # check password against current hashed value, then update if valid
        if check_password(current_pass, user['password']):
            query = {'public_id': id}
            replace = {"$set": {'password': get_hashed_password(new_pass)}}
            user_collection.update_one(query, replace)

        return render_template('/login.html')

    # allow appointment providers to set their availability


@app.route("/setSchedule/<id>", methods=['POST', 'GET'])
def setSchedule(id):
    if request.method == 'GET':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        if user['role'] == "user":
            return redirect(url_for('createAppointment', id=id))
        return render_template('/setSchedule.html', id=id, user=user)
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

            # calculate the date of the next monday
            monday = today + timedelta(days=(7 - today.weekday()) % 7)

            # Loop through the schedule data and insert appointments for the specified number of weeks
            # Generate appointments for each week
            for i in range(int(request.form['numweeks'])):
                for day, start_time, end_time in schedule_data:
                    if start_time and end_time:
                        # Determine the date for this day of the week
                        currentdate = monday + timedelta(
                            days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(
                                day))
                        print(timedelta(
                            days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(
                                day)))
                        appointment_collection.insert_one(
                            {'start_time': currentdate.strftime('%Y-%m-%d') + ' ' + start_time,
                             'end_time': currentdate.strftime('%Y-%m-%d') + ' ' + end_time,
                             'date': currentdate.strftime('%A, %Y-%m-%d'), 'customer_name': '', 'provider_name': name,
                             'location': 'N/A', 'Notes': 'N/A'})
                monday = monday + timedelta(days=7)
            return redirect(url_for('home', id=id))
        except Exception as e:
            return "Error in query operation " + str(e)


# create an appointment
@app.route("/createAppointment/<id>", methods=['POST', 'GET'])
def createAppointment(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    appointment_collection = mongo.db.Appointments
    myquery = {'$and': [{'customer_name': ''}, {'start_time': {'$gt': datetime.datetime.now().strftime('%Y-%m-%d')}}]}
    all_appointments = appointment_collection.find(myquery).sort("start_time", 1)

    # pass in the list of appointments and user info
    if request.method == 'GET':
        return render_template('/createAppointment.html', id=id, appointments=all_appointments, user=user)
    else:
        try:
            return redirect(url_for('home', id=id))
        except Exception as e:
            return "Error in query operation " + str(e)


# add appointment
@app.route("/addAppointment/")
def addAppointment():
    appId = request.args.get('appId')
    user_id = request.args.get('user_id')
    appointment_collection = mongo.db.Appointments
    user_collection = mongo.db.Users
    user_query = {'public_id': user_id}
    user = user_collection.find_one(user_query)
    myquery = {'_id': ObjectId(appId)}
    set_appointment = {"$set": {'customer_name': user['name']}}
    appointment_collection.update_one(myquery, set_appointment)

    return redirect(url_for('home', id=user_id))


# delete an appointment
@app.route("/deleteAppointment/<id>/<appointmentid>", methods=['POST', 'GET'])
def deleteAppointment(id, appointmentid):
    user_query = {'public_id': id}
    user_collection = mongo.db.Users
    user = user_collection.find_one(user_query)
    appointment_collection = mongo.db.Appointments
    myquery = {'_id': ObjectId(appointmentid)}
    if user['role'] == 'provider':
        appointment_collection.delete_one(myquery)
        return redirect(url_for('providerHome', id=id))
    else:
        set_appointment = {"$set": {'customer_name': ''}}
        appointment_collection.update_one(myquery, set_appointment)
        return redirect(url_for('userHome', id=id))


if __name__ == '__main__':
    app.run(debug=True)
