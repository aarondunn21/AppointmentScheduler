from flask import Flask, render_template, redirect, url_for, request
from extensions import mongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://admin:Password123@appointmentscheduler.ikvbn6u.mongodb.net/mydb?retryWrites=true&w=majority'
# Database location on Atlas
mongo.init_app(app)

@app.route("/")
def home():
    user_collection = mongo.db.Users
    users_list = user_collection.find()
    return render_template('index.html', users=users_list)

@app.route("/add_user", methods =['POST'])
def add_user():
    user_collection = mongo.db.Users
    # Table to add to
    user_item = request.form.get('add-user')
    # get name from html input form
    user_collection.insert_one({'text' : user_item})
    # add name into table
    return redirect(url_for('home'))

@app.route("/delete_user/<id>")
def delete_user(id):
    print(id)
    user_collection = mongo.db.Users
    my_query = {'_id' : ObjectId(id)}
    user_collection.delete_one(my_query)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)