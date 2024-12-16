import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# REGISTER ROUTE
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # User submitted form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate submission
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        # Insert user into database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user(username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)

    # Initial page load
    return render_template('auth/register.html')


# LOGIN ROUTE
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # User submitted form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Check if user exists and user credentials
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'

        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        # Valid user
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    # Initial page load
    return render_template('auth/login.html')


# SESSION CHECK
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    # No user logged in
    if user_id is None:
        g.user = None

    # User logged in
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()


# LOGOUT ROUTE
@bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('index'))