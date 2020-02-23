#!/usr/bin/python3
from flask import Flask, request,jsonify, render_template, send_from_directory,session,redirect,url_for
import os
from flask_login import LoginManager
#from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField, SubmitField
from flask_mysqldb import MySQL
import MySQLdb
import re

app = Flask(__name__)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'zesty_user'
app.config['MYSQL_PASSWORD'] = 'Z3$tyU$3r54'
app.config['MYSQL_DB'] = 'Zesty'
mysql = MySQL(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/styles'),'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET', 'POST'])
def signin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        msg=''
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Zesty.Users WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in users table in database
        if account:
            # Create session
            session['loggedin'] = True
            session['userID'] = account['userID']
            session['email'] = account['email']
            msg='Login Successful'

            # Redirect to recipes page
            return redirect(url_for('yourRecipes'))
        else:
            # Account doesnt exist or email/password incorrect
            msg = 'Incorrect email/password!'
    # Show the login form with message (if any)
    return render_template('screens/signin.html', msg=msg)
   
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'fullName' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullName = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
  
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Zesty.Users WHERE email = %s', [email])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z ]+', fullName):
            msg = 'Full Name must contain only characters!'
        elif not fullName or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO Zesty.Users (fullName, email, password) VALUES (%s, %s, %s)', (fullName, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('yourRecipes'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('screens/signup.html', msg=msg)


@app.route('/yourRecipes', methods=['GET', 'POST'])
def yourRecipes():
    cur = mysql.connection.cursor()
    user=session['userID']
    cur.execute('SELECT fullName FROM Zesty.Users where userID=%s', [user])
    name = cur.fetchone()
    cur.execute('SELECT recipeID, recipeName FROM Zesty.RecipeInfo where userID=%s', [user])
    recipes=cur.fetchall()
    return render_template("screens/yourrecipes.html", name=name[0], recipeCard=recipes)

@app.route('/viewRecipe', methods=['GET'])
def viewRecipe():
    cur = mysql.connection.cursor()
    user=session['userID']
    recipeID = request.args.get('recipeID')
    cur.execute('SELECT recipeName, recipeDescription, preparationTime, yield, methods, recipeTag FROM Zesty.RecipeInfo where userID=%s and recipeID=%s', [user, recipeID])
    recipeInfo=cur.fetchone()
    return render_template("screens/viewrecipe.html", recipeName=recipeInfo[0],recipeID=recipeID, recipeDescription=recipeInfo[1], preparationTime=recipeInfo[3], recipeMethods=recipeInfo[4], recipeTag=recipeInfo[5])

@app.route('/addRecipe', methods=['GET'])
def addRecipe():
    return render_template("screens/addrecipe.html")

@app.route('/editRecipe', methods=['GET', 'POST'])
def editRecipe():
    cur = mysql.connection.cursor()
    user=session['userID']
    recipeID = request.args.get('recipeID')
    cur.execute('SELECT recipeName,recipeDescription, preparationTime, yield, methods FROM Zesty.RecipeInfo where userID=%s and recipeID=%s', [user, recipeID])
    recipeInfo=cur.fetchone()
    return render_template("screens/editrecipe.html", recipeName=recipeInfo[0], recipeDescription=recipeInfo[1], preparationTime=recipeInfo[2], recipeYield=recipeInfo[3], recipeMethods=recipeInfo[4])

@app.route('/groceries', methods=['GET'])
def groceries():
    return render_template("screens/groceries.html")


@app.route('/profile', methods=['GET'])
def profile():
    cur = mysql.connection.cursor()
    user=session['userID']
    cur.execute('SELECT fullName, email FROM Zesty.Users where userID=%s', [user])
    rv = cur.fetchone()
    return render_template("screens/profile.html", name=rv[0], email=rv[1])
   

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
