from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms.auth_forms import RegisterForm, LoginForm, SearchForm
from forms.recipe_forms import RecipeForm
from MySQLdb.cursors import DictCursor

import base64
from app import mysql, login_manager

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, password_hash FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(*user)
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password_hash = generate_password_hash(form.password.data)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                    (username, email, password_hash))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (form.email.data,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[3], form.password.data):
            user_obj = User(*user)
            login_user(user_obj)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('auth.recipes'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    # Search form handling
    form = SearchForm()
    search_query = request.args.get('search', '')  # Capture search term from URL

    # fetch recipes
    query = """SELECT r.*, c.name as category_name 
    FROM recipes r 
    LEFT JOIN categories c ON r.category_id = c.id
    WHERE r.title LIKE %s OR r.ingredients LIKE %s OR c.name LIKE %s
"""
    params = [f'%{search_query}%', f'%{search_query}%', f'%{search_query}%']

    # If no search hit then give all
    if not search_query:
        query = """
    SELECT r.*, c.name as category_name 
    FROM recipes r 
    LEFT JOIN categories c ON r.category_id = c.id
"""
        params = []


    # Execute the query
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute(query, params)
    recipes = cursor.fetchall()
    #print(recipes)
    return render_template('recipes.html', form=form, recipes=recipes)

@auth_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_recipe():
    form = RecipeForm()

     # Load category choices from DB before validation or rendering
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    form.category.choices = categories  # Important: (id, name) pairs
    if form.validate_on_submit():
        title = form.title.data
        ingredients = form.ingredients.data
        instructions = form.instructions.data
        category_id = form.category.data
        image_data = form.image.data.read() if form.image.data else None

        cursor = mysql.connection.cursor()
        cursor.execute("""
        INSERT INTO recipes (user_id, title, ingredients, instructions, image,category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user.id, title, ingredients, instructions, image_data,category_id))

        mysql.connection.commit()
        cursor.close()

        flash('Recipe submitted successfully!', 'success')
        return redirect(url_for('auth.recipes'))
    
    return render_template('submit_recipe.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))