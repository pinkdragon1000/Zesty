#!/usr/bin/python3
from flask import Flask, request,jsonify, render_template, send_from_directory
import os

#from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'zesty_user'
app.config['MYSQL_PASSWORD'] = 'Z3$tyU$3r54'
app.config['MYSQL_DB'] = 'Zesty'
mysql = MySQL(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/styles'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/')
def login():
    return render_template("screens/signin.html")
    

@app.route('/users') 
def users()  
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM Zesty.Users''')
    rv = cur.fetchall()
    return str(rv)
    

@app.route('/signup')
def signup():
    return render_template("screens/signup.html")


@app.route('/yourRecipes', methods=['GET'])
def youRecipes():
    return render_template("screens/yourrecipes.html")

@app.route('/viewRecipe', methods=['GET'])
def recipe():
    return render_template("screens/viewrecipe.html")

@app.route('/addRecipe', methods=['GET'])
def addRecipe():
    return render_template("screens/addrecipe.html")

@app.route('/editRecipe', methods=['GET'])
def editRecipe():
    return render_template("screens/editRecipe.html")

@app.route('/groceries', methods=['GET'])
def groceries():
    return render_template("screens/groceries.html")
    
@app.route('/profile', methods=['GET'])
def profile():
    return render_template("screens/profile.html")



if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)