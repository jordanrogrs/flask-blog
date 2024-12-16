from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint('blog', __name__)

# INDEX ROUTE
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# GET POST FUNCTION
def get_post(id, check_author=True):
    # Select post based on author id
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,),
    ).fetchone()

    # Validate request
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post


# CREATE ROUTE
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    # User submits form
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # Validate submission
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        
        # Else no errors
        else:
            # Insert post into database
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES(?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    # Initial page load
    return render_template('blog/create.html')


# UPDATE ROUTE
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # Get post you want to update
    post = get_post(id)

    # User submitted form
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # Validate submission
        if not title:
            error = 'Title is required.'
       
        if error is not None:
            flash(error)
        
        # Else no errors
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    # Initial page load
    return render_template('blog/update.html', post=post)


# DELETE ROUTE
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
    
