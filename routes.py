#!/usr/bin/python3
from flask import Flask
from flask import request,jsonify
from flask import render_template

app = Flask(__name__)
@app.route('/')
def login():
    return render_template("signin.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/yourRecipes', methods=['GET'])
def youRecipes():
    return render_template("yourrecipes.html")


if __name__ == '__main__':
    app.run(use_reloader=True)