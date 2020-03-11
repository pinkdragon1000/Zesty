#!/usr/bin/python3
from flask import Flask, request,jsonify, render_template, send_from_directory,session,redirect,url_for
import os
from flask_login import LoginManager
from flask_mysqldb import MySQL
import MySQLdb
import re
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'zesty_user'
app.config['MYSQL_PASSWORD'] = 'Z3$tyU$3r54'
app.config['MYSQL_DB'] = 'Zesty'
mysql = MySQL(app)
passwordSalt = "5gz"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/styles'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect("/", code=302)

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
        # Hashed password
        dbPassword = password+passwordSalt
        hashedObject= hashlib.md5(dbPassword.encode())
        password=hashedObject.hexdigest()       
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
    return render_template('screens/signin.html', validationMessage=msg, pageName="Sign In", formAction="/", path=request.path)
   
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Getting user information from the frontend signup form
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
        elif len(password) < 8:
            msg = 'Password must be at least 8 characters'
        elif not fullName or not password or not email:
            msg = 'Please fill out the form!'
        elif re.search('[0-9]',password) is None:
            msg = 'Make sure your password has a number in it'
        elif re.search('[A-Z]',password) is None:
            msg = 'Make sure your password has a capital letter in it'
        else:
            # Hashing Password
            dbPassword = password+passwordSalt
            hashedObject= hashlib.md5(dbPassword.encode())
            password=hashedObject.hexdigest()
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO Zesty.Users (fullName, email, password) VALUES (%s, %s, %s)', (fullName, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            cursor.execute('SELECT * FROM Zesty.Users WHERE email = %s AND password = %s', (email, password))
            account = cursor.fetchone()
            session['loggedin'] = True
            session['userID'] = account['userID']
            return redirect(url_for('yourRecipes'))
    # Show registration form with message (if any)
    return render_template('screens/signup.html', validationMessage=msg, pageName="Sign Up", formAction="/signup", path=request.path)

@app.route('/yourRecipes', methods=['GET', 'POST'])
def yourRecipes():
    if 'loggedin' not in session:
        return redirect("/", code=302)
    cur = mysql.connection.cursor()
    user=session['userID']
    search=""
    showPublic = True
    # Recipe Search
    if request.method=='POST':
        search=request.form.get('search')
        # Checks to see if the showPublic toggle is on or off
        showPublic= True if request.form.get('showPublic') == 'on' else False
    cur.execute('SELECT fullName FROM Zesty.Users where userID=%s', [user])
    name = cur.fetchone()
    # If a search query is typed in
    if search != "":
        searchQuery = '%' + search + '%'
        if showPublic:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where (userID=%s or ispublic=1) and recipeName or recipeTag like %s', [user,searchQuery])
        else:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where (userID=%s) and recipeName or recipeTag like %s', [user,searchQuery])
    # If a search query is not typed in
    else:
        if showPublic:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where (userID=%s or ispublic=1)' , [user])
        else:
            cur.execute('SELECT recipeID, recipeName, recipeImage FROM Zesty.RecipeInfo where userID=%s', [user])
    recipes=cur.fetchall()
    return render_template("screens/yourrecipes.html", recipeCard=recipes, pageName=name[0]+"'s Recipes", search=search, showPublic="checked" if showPublic else "", formAction="/yourRecipes")

@app.route('/viewRecipe', methods=['GET', 'POST'])
def viewRecipe():
    if 'loggedin' not in session:
        return redirect("/", code=302)
    cur = mysql.connection.cursor()
    user=session['userID']
    recipeID = request.args.get('recipeID')
    if request.method=='POST':
        inGroceries=request.form.get('inGroceries')
        # Inserts ingredients into grocery list if the toggle is on
        if inGroceries=="on":
            cur.execute('INSERT INTO Zesty.GroceryList (userID, recipeID) values (%s,%s)', [user, recipeID])
        # Deletes ingredients from grocery list if the toggle is off
        else:
            cur.execute('DELETE FROM Zesty.GroceryList where userID=%s and recipeID=%s',[user, recipeID])
        mysql.connection.commit()
        

    cur.execute('SELECT count(*) from Zesty.GroceryList where userID=%s and recipeID=%s', [user, recipeID])
    inGroceries='checked' if cur.fetchone()[0]!=0 else 'unchecked'

    cur.execute('SELECT recipeName, recipeDescription, preparationTime, yield, methods, recipeTag, recipeImage, userID FROM Zesty.RecipeInfo where (userID=%s or ispublic=1) and recipeID=%s', [user, recipeID])
    recipeInfo=cur.fetchone()
    # Checking to see if the recipe is yours. If this is not your recipe you won't be able to edit that information
    isMine = (user==recipeInfo[7])

    # Replacing newlines with a space (br) for ingredients
    if(recipeInfo[4] !=None):
        methodSplit=recipeInfo[4].replace('\n', '<br>')
    else:
        methodSplit=recipeInfo[4]
    # Selecting ingredient information from the table
    cur.execute('SELECT ingredientDescription,ingredientAmount, ingredientUnit FROM Zesty.RecipeIngredients where recipeID=%s', [recipeID])
    ingredientInfo=cur.fetchall()
    # Making sure there is at least one ingredient box with recipeDescription, recipeAmount, and recipeUnit
    if len(ingredientInfo) == 0:
        ingredientInfo = [['','','']]  
    return render_template("screens/viewrecipe.html", pageName=recipeInfo[0],recipeID=recipeID, recipeDescription=recipeInfo[1], preparationTime=recipeInfo[2], recipeYield=recipeInfo[3], recipeMethods=methodSplit, recipeTag=recipeInfo[5], recipeImage=recipeInfo[6], ingredientInfo=ingredientInfo, formAction=url_for("viewRecipe",recipeID=recipeID), inGroceries=inGroceries, isMine=isMine)

#Upload folder for images
UPLOAD_FOLDER = 'static/styles/recipeimages/'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@app.route('/addRecipe', methods=['GET', 'POST'])
def addRecipe():
    if 'loggedin' not in session:
        return redirect("/", code=302)
    msg=""
    recipeName=""
    recipeDescription=""
    preparationTime=""
    recipeYield=""
    recipeMethods=""
    recipeTag=""
    ingredientInfo=[['','','']]
    cur = mysql.connection.cursor()
    user=session['userID']
    recipePermission="unchecked"
    if request.method=='POST':
        recipeImage = ''
        if request.files:
            file = request.files['recipeImage']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file and file.filename != '':
                recipeFileName = file.filename
                # Generate a unique filename for the uploaded image
                recipeFileName = str(uuid.uuid4())  
                file.save(os.path.join(UPLOAD_FOLDER, recipeFileName))
                recipeImage=UPLOAD_FOLDER+recipeFileName
        # Getting recipe information from the frontend
        recipeName=request.form.get('recipeName','')
        recipeDescription=request.form.get('recipeDescription', '')
        preparationTime=request.form.get('preparationTime', '')
        recipeYield=request.form.get('recipeYield', '')
        recipeMethods=request.form.get('recipeMethods', '')
        recipeTag=request.form.get('recipeTag', '')
        recipePermission=request.form.get('recipePermission', '')

        recipePermission= 1 if request.form.get('recipePermission') == 'on' else 0

        if recipeName=="":
            msg="Please enter in a valid recipe name"
        elif recipeMethods=="":
            msg="Please enter in valid recipe methods"
        else:
            cur.execute('INSERT into Zesty.RecipeInfo (recipeName, recipeDescription, preparationTime, yield, methods, recipeTag, ispublic, recipeImage, userID) values (%s,%s,%s,%s,%s, %s, %s, %s, %s)',[recipeName, recipeDescription, preparationTime, recipeYield, recipeMethods, recipeTag, recipePermission, recipeImage, user])
            mysql.connection.commit()
            cur.execute("SELECT LAST_INSERT_ID()")
            recipeID = cur.fetchone()[0]

            cur.execute('DELETE FROM Zesty.RecipeIngredients where recipeID = %s;',[recipeID])
            mysql.connection.commit()

            ingredientAmounts = request.form.getlist('ingredientAmount')
            ingredientUnits = request.form.getlist('ingredientUnit')
            ingredientNames = request.form.getlist('ingredientName')

            ingredientInfo = [[a,b,c] for (a,b,c) in zip(ingredientAmounts,ingredientUnits,ingredientNames)]
            if len(ingredientInfo) == 0:
                ingredientInfo=[['','','']]

            for (amount, unit, name) in zip(ingredientAmounts,ingredientUnits,ingredientNames):
                cur.execute("INSERT INTO Zesty.RecipeIngredients (recipeID, ingredientDescription, ingredientAmount, ingredientUnit) values (%s, %s, %s, %s);",[recipeID,name,amount,unit])
            mysql.connection.commit()
    return render_template("screens/addrecipe.html", formAction="/addRecipe", editableTitle=True, formInTemplate=True, validationMessage=msg, pageName=recipeName, recipeDescription=recipeDescription, preparationTime=preparationTime, recipeYield=recipeYield, recipeMethods=recipeMethods, recipeTag=recipeTag, recipePermission=recipePermission, ingredientInfo=ingredientInfo)

@app.route('/editRecipe', methods=['GET', 'POST'])
def editRecipe():
    if 'loggedin' not in session:
        return redirect("/", code=302)
    msg=''
    user=session['userID']
    recipeID = request.args.get('recipeID')
    
    if request.method=='POST':
        recipeImageUrl = request.form.get('recipeImageUrl')
        if request.files:
            file = request.files['recipeImage']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file and file.filename != '':
                recipeFileName = file.filename
                recipeFileName = str(uuid.uuid4())  # Generate a unique filename for the uploaded image                
                file.save(os.path.join(UPLOAD_FOLDER, recipeFileName))
                recipeImageUrl=UPLOAD_FOLDER+recipeFileName
        cur = mysql.connection.cursor()
        deleteRecipe=request.form.get('deleteRecipe')
        if deleteRecipe=="1":
            cur.execute("Delete from RecipeInfo where recipeID=%s", [recipeID])
            mysql.connection.commit()
            return redirect(url_for("yourRecipes"))
       
        # Getting recipe information from the frontend
        recipeName=request.form.get('recipeName')
        recipeDescription=request.form.get('recipeDescription')
        preparationTime=request.form.get('preparationTime')
        recipeYield=request.form.get('recipeYield')
        recipeMethods=request.form.get('recipeMethods')
        recipeTag=request.form.get('recipeTag')
        recipePermission=request.form.get('recipePermission')
        recipePermission= 1 if request.form.get('recipePermission') == 'on' else 0
        cur.execute("UPDATE Zesty.RecipeInfo SET recipeName=%s, recipeDescription=%s, preparationTime=%s, yield=%s, methods=%s, recipeTag=%s, ispublic=%s, recipeImage=%s where userID=%s and recipeID=%s", [recipeName, recipeDescription, preparationTime, recipeYield, recipeMethods, recipeTag, recipePermission, recipeImageUrl, user, recipeID])

        cur.execute('DELETE FROM Zesty.RecipeIngredients where recipeID = %s;',[recipeID])
        mysql.connection.commit()
         # Getting ingredient information from the frontend
        ingredientAmounts = request.form.getlist('ingredientAmount')
        ingredientUnits = request.form.getlist('ingredientUnit')
        ingredientNames = request.form.getlist('ingredientName')

        for (amount, unit, name) in zip(ingredientAmounts,ingredientUnits,ingredientNames):
            cur.execute("INSERT INTO Zesty.RecipeIngredients (recipeID, ingredientDescription, ingredientAmount, ingredientUnit) values (%s, %s, %s, %s);",[recipeID,name,amount,unit])
        mysql.connection.commit()

    selectCur = mysql.connection.cursor()
    selectCur.execute('SELECT recipeName,recipeDescription, preparationTime, yield, methods, recipeTag, ispublic, recipeImage FROM Zesty.RecipeInfo where userID=%s and recipeID=%s', [user, recipeID])
    recipeInfo=selectCur.fetchone()
    if(recipeInfo[6]==1):
        recipePermission="checked"
    else:
        recipePermission="unchecked"

    selectCur.execute('SELECT ingredientDescription,ingredientAmount, ingredientUnit FROM Zesty.RecipeIngredients where recipeID=%s', [recipeID])
    ingredientInfo=list(selectCur.fetchall())
    if len(ingredientInfo) == 0:
        ingredientInfo = [['','','']]  # make sure we have at least one
    ingredientInfo = [list(i) for i in ingredientInfo]
    return render_template("screens/editrecipe.html", pageName=recipeInfo[0], recipeDescription=recipeInfo[1], preparationTime=recipeInfo[2], recipeYield=recipeInfo[3], recipeMethods=recipeInfo[4], recipeTag=recipeInfo[5], recipePermission=recipePermission, recipeImageUrl=recipeInfo[7], formAction=url_for("editRecipe",recipeID=recipeID),recipeID=recipeID, ingredientInfo=ingredientInfo, editableTitle=True, formInTemplate=True,  validationMessage=msg)

@app.route('/groceries', methods=['GET', 'POST'])
def groceries():
    if 'loggedin' not in session:
        return redirect("/", code=302)
    cur = mysql.connection.cursor()
    user=session['userID']
    if request.method == 'POST':
        cur.execute('DELETE FROM Zesty.GroceryList where userID=%s', [user])
        mysql.connection.commit()
    cur.execute('SELECT DISTINCT ingredientDescription from Zesty.RecipeIngredients join Zesty.GroceryList on RecipeIngredients.recipeID=GroceryList.recipeID and userID=%s ORDER BY ingredientDescription', [user])
    groceryListIngredients=cur.fetchall()
    return render_template("screens/groceries.html", pageName="Groceries", groceryListIngredients=groceryListIngredients)


@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'loggedin' not in session:
        return redirect("/", code=302)
    msg=''
    user=session['userID']
    if request.method == 'POST':
        update_cur = mysql.connection.cursor()
        # Getting profile information from the frontend
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        if name=="":
            msg="Please enter in a valid name"
        elif email=="":
            msg="Please enter in a valid email"
        else:
            try:
                update_cur.execute("UPDATE Zesty.Users SET fullName=%s, email=%s where userID=%s", [name, email, user])
                mysql.connection.commit()
            except MySQLdb.Error:
                msg = 'This email is already in use.  Please use another.'
    cur = mysql.connection.cursor()
    cur.execute('SELECT fullName, email FROM Zesty.Users where userID=%s', [user])
    profileInfo = cur.fetchone()
    return render_template("screens/profile.html", name=profileInfo[0], email=profileInfo[1], pageName="Profile", formAction="/profile", formInTemplate=True, validationMessage=msg)

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
