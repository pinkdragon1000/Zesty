#!/usr/bin/python3
from flask import Flask
from flask import request,jsonify
from flask import render_template
from flask import send_from_directory
import os

app = Flask(__name__)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/styles'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/')
def login():
    return render_template("signin.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/yourRecipes', methods=['GET'])
def youRecipes():
    return render_template("screens/yourrecipes.html")

@app.route('/recipe', methods=['GET'])
def recipe():
    return render_template("screens/recipe.html")

@app.route('/addRecipe', methods=['GET'])
def addRecipe():
    return render_template("screens/addrecipe.html")

@app.route('/editRecipe', methods=['GET'])
def editRecipe():
    return render_template("screens/editRecipe.html")
    
@app.route('/profile', methods=['GET'])
def profile():
    return render_template("screens/profile.html")



if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)