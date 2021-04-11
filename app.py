import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/get_started")
def get_started():
    return render_template("get_started.html")

@app.route("/recipes")
def recipes():

    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)

@app.route("/recipe/<recipe_name>")
def recipe(recipe_name):

    recipe = mongo.db.recipes.find_one(
        {"recipe_name": recipe_name }
    )

    return render_template("recipe.html", recipe=recipe)
    

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("sign_up"))

        register = {
            "username": request.form.get("username"),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username")
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username")
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    recipes = mongo.db.recipes.find(
        {"author": username }
    )

    if session["user"]:
        return render_template("profile.html", username=username, recipes=recipes)
    
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    if request.method == "POST":
        
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "ingredients": [request.form.get("ingredient1"),request.form.get("ingredient2"),request.form.get("ingredient3"),request.form.get("ingredient4"),request.form.get("ingredient5"),request.form.get("ingredient6"),request.form.get("ingredient7")],
            "method": [request.form.get("step1"),request.form.get("step2"),request.form.get("step3"),request.form.get("step4"),request.form.get("step5"),request.form.get("step6"),request.form.get("step7")],
            "author": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("create_recipe.html")

@app.route("/edit_recipe/<username>/<recipe_name>", methods=["GET", "POST"])
def edit_recipe(username, recipe_name):

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    recipe_name = mongo.db.recipes.find_one(
        {"recipe_name": recipe_name }
    )

    if request.method == "POST":
        
        edited_recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "ingredients": [request.form.get("ingredient1"),request.form.get("ingredient2"),request.form.get("ingredient3"),request.form.get("ingredient4"),request.form.get("ingredient5"),request.form.get("ingredient6"),request.form.get("ingredient7")],
            "method": [request.form.get("step1"),request.form.get("step2"),request.form.get("step3"),request.form.get("step4"),request.form.get("step5"),request.form.get("step6"),request.form.get("step7")],
            "author": session["user"]
        }
        mongo.db.recipes.update(recipe_name, edited_recipe)
        flash("Recipe Successfully Edited")
        return redirect(url_for("profile", username=session["user"]))


    return render_template("edit_recipe.html", username=username, recipe_name=recipe_name)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)