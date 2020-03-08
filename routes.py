


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
    search=""
    showPublic = True
    if request.method=='POST':
        search=request.form.get('search')
        showPublic= True if request.form.get('showPublic') == 'on' else False
    cur.execute('SELECT fullName FROM Zesty.Users where userID=%s', [user])
    name = cur.fetchone()
    if search != "":
        searchQuery = '%' + search + '%'
        if showPublic:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where (userID=%s or ispublic=1) and recipeName like %s', [user,searchQuery])
        else:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where (userID=%s) and recipeName like %s', [user,searchQuery])
    else:
        if showPublic:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where (userID=%s or ispublic=1)' , [user])
        else:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where userID=%s', [user])
    recipes=cur.fetchall()
    return render_template("screens/yourrecipes.html", recipeCard=recipes, recipeName=name[0]+"'s Recipes", search=search, showPublic="checked" if showPublic else "")


@app.route('/viewRecipe', methods=['GET'])
def viewRecipe():
    cur = mysql.connection.cursor()
    user=session['userID']
    recipeID = request.args.get('recipeID')
    cur.execute('SELECT recipeName, recipeDescription, preparationTime, yield, methods, recipeTag, recipeImage FROM Zesty.RecipeInfo where (userID=%s or ispublic=1) and recipeID=%s', [user, recipeID])
    recipeInfo=cur.fetchone()
    if(recipeInfo[4] !=None):
        methodSplit=recipeInfo[4].replace('\n', '<br>')
    else:
        methodSplit=recipeInfo[4]
    return render_template("screens/viewrecipe.html", recipeName=recipeInfo[0],recipeID=recipeID, recipeDescription=recipeInfo[1], preparationTime=recipeInfo[3], recipeMethods=methodSplit, recipeTag=recipeInfo[5], recipeImage=recipeInfo[6])

UPLOAD_FOLDER = 'static/styles/recipeimages/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@app.route('/addRecipe', methods=['GET', 'POST'])
def addRecipe():
    cur = mysql.connection.cursor()
    user=session['userID']
    recipePermission="unchecked"
    if request.method=='POST':
        recipeImage = ''
        if request.files:
            print(request.files)
            file = request.files['recipeImage']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file and file.filename != '':
                recipeFileName = file.filename
                file.save(os.path.join(UPLOAD_FOLDER, recipeFileName))
                recipeImage=UPLOAD_FOLDER+recipeFileName
        recipeName=request.form.get('recipeName')
        recipeDescription=request.form.get('recipeDescription')
        preparationTime=request.form.get('preparationTime')
        recipeYield=request.form.get('recipeYield')
        recipeMethods=request.form.get('recipeMethods')
        recipeTag=request.form.get('recipeTag')
        recipePermission=request.form.get('recipePermission')
        if(recipePermission=="on"):
            recipePermission=1
        else:
            recipePermission=0
        cur.execute('INSERT into Zesty.RecipeInfo (recipeName, recipeDescription, preparationTime, yield, methods, recipeTag, ispublic, recipeImage, userID) values (%s,%s,%s,%s,%s, %s, %s, %s, %s)',[recipeName, recipeDescription, preparationTime, recipeYield, recipeMethods, recipeTag, recipePermission, recipeImage, user])
        mysql.connection.commit()
        '''
        recipePermission=cur.fetchone()[6]
        if(recipePermission==1):
            recipePermission="checked"
        else:
            recipePermission="unchecked"

        '''

        ingredientAmounts = request.form.getlist('ingredientAmount')
        ingredientUnits = request.form.getlist('ingredientUnit')
        ingredientNames = request.form.getlist('ingredientName')

        for (amount, unit, name) in zip(ingredientAmounts,ingredientUnits,ingredientNames):
            print((amount, unit, name))

        '''
        cur.execute('SELECT recipeID from Zesty.RecipeInfo')
        
        recipeID=cur.fetchone()[0]
        print(recipeID)
    
        ingredientDescription=request.form.get("ingredientName")
        print(ingredientDescription)
        ingredientAmount=request.form.get("ingredientAmount")
        print(ingredientAmount)
        ingredientUnit=request.form.get("ingredientUnit")
        print(ingredientUnit)
        cur.execute('INSERT into Zesty.RecipeIngredients (recipeID, ingredientDescription, ingredientAmount, ingredientUnit) values (%s, %s, %s, %s)',[recipeID, ingredientDescription,ingredientAmount, ingredientUnit])
        mysql.connection.commit()
        '''
    return render_template("screens/addrecipe.html", formAction="/addRecipe", recipePermission=recipePermission)

@app.route('/editRecipe', methods=['GET', 'POST'])
def editRecipe():
    user=session['userID']
    recipeID = request.args.get('recipeID')
    
    if request.method=='POST':
        recipeImage = ''
        if request.files:
            file = request.files['recipeImage']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file and file.filename != '':
                recipeFileName = file.filename
                file.save(os.path.join(UPLOAD_FOLDER, recipeFileName))
                recipeImage=UPLOAD_FOLDER+recipeFileName
        cur = mysql.connection.cursor()
        deleteRecipe=request.form.get('deleteRecipe')
        print("delete+", deleteRecipe)
        if deleteRecipe=="1":
            cur.execute("Delete from RecipeInfo where recipeID=%s", [recipeID])
            mysql.connection.commit()
            return redirect(url_for("yourRecipes"))

        recipeName=request.form.get('recipeName')
        recipeDescription=request.form.get('recipeDescription')
        preparationTime=request.form.get('preparationTime')
        recipeYield=request.form.get('recipeYield')
        recipeMethods=request.form.get('recipeMethods')
        recipeTag=request.form.get('recipeTag')
        recipePermission=request.form.get('recipePermission')
        if(recipePermission=="on"):
            recipePermission=1
        else:
            print("recipePermission",recipePermission)
            recipePermission=0
        cur.execute("UPDATE Zesty.RecipeInfo SET recipeName=%s, recipeDescription=%s, preparationTime=%s, yield=%s, methods=%s, recipeTag=%s, ispublic=%s, recipeImage=%s where userID=%s and recipeID=%s", [recipeName, recipeDescription, preparationTime, recipeYield, recipeMethods, recipeTag, recipePermission, recipeImage, user, recipeID])
        mysql.connection.commit()
    selectCur = mysql.connection.cursor()
    selectCur.execute('SELECT recipeName,recipeDescription, preparationTime, yield, methods, recipeTag, ispublic, recipeImage FROM Zesty.RecipeInfo where userID=%s and recipeID=%s', [user, recipeID])
    recipeInfo=selectCur.fetchone()
    if(recipeInfo[6]==1):
        recipePermission="checked"
    else:
        recipePermission="unchecked"
    '''
    selectCur.execute('SELECT ingredientDescription,ingredientAmount, ingredientUnit FROM Zesty.RecipeInfo where recipeID=%s', [recipeID])
    ingredientInfo=selectCur.fetchall()
    '''
    return render_template("screens/editrecipe.html", recipeName=recipeInfo[0], recipeDescription=recipeInfo[1], preparationTime=recipeInfo[2], recipeYield=recipeInfo[3], recipeMethods=recipeInfo[4], recipeTag=recipeInfo[5], recipePermission=recipePermission, recipeImage=recipeInfo[7], formAction=url_for("editRecipe",recipeID=recipeID))

@app.route('/groceries', methods=['GET'])
def groceries():
    return render_template("screens/groceries.html", recipeName="Groceries")


@app.route('/profile', methods=['GET','POST'])
def profile():
    user=session['userID']
    if request.method == 'POST':
        update_cur = mysql.connection.cursor()
        name = request.form.get('name')
        email = request.form.get('email')
        update_cur.execute("UPDATE Zesty.Users SET fullName=%s, email=%s where userID=%s", [name, email, user])
        mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute('SELECT fullName, email FROM Zesty.Users where userID=%s', [user])
    profileInfo = cur.fetchone()
    return render_template("screens/profile.html", name=profileInfo[0], email=profileInfo[1], recipeName="Profile")

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
