import os
import glob
from werkzeug.utils import secure_filename

import sqlalchemy.exc
from flask import Flask, session, redirect, jsonify, render_template, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy import func

from .db import init_db, db, close_db
from .models import User, Post, Likes


full_project_path = os.path.dirname(os.path.realpath(__file__))

# create and configure the app
app = Flask(__name__, instance_path=full_project_path)

# load the instance config
app.config.from_pyfile('config.py', silent=True)
app.app_context()

# ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# configure the database initialization and teardown
db.init_app(app)
app.cli.add_command(init_db)
app.teardown_appcontext(close_db)

# Note: profile photo upload removed to avoid schema changes. Profiles store only simple fields.

# --- ADD: Avatar configuration (file-based avatars; no DB changes) ---
AVATAR_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'images', 'avatars')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(AVATAR_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def get_avatar_url_for_user_id(uid):
    for ext in ALLOWED_EXT:
        candidate = os.path.join(AVATAR_FOLDER, f"user_{uid}.{ext}")
        if os.path.exists(candidate):
            return url_for('static', filename=f"images/avatars/user_{uid}.{ext}")
    return None
# --- END ADD ---


@app.route('/')
def index():
    user = None
    posts = None
    like_counts = None
    
    # If the user is logged in
    if "email" in session:
        user = db.session.execute(db.select(User).filter_by(email=session["email"])).scalar_one()
        # This is another way to query a user
        # user= User.query.filter(User.email == session["email"]).first()

        like_count_subq = db.select(func.count(Likes.id).label('likes'), Likes.post_id).group_by(Likes.post_id).subquery()
        posts_result = db.session.execute(db.select(Post, like_count_subq.c.likes).outerjoin_from(Post, like_count_subq).order_by(Post.created_at))

        posts = []
        like_counts = []
        for post_result in posts_result:
            post, like_count = post_result
            posts.append(post)
            like_counts.append(like_count)

    return render_template('index.html', current_user=user, all_posts=posts, likes=like_counts)


@app.route('/sign-up', methods=['POST'])
def sign_up():
    user = User(
        request.form['firstName'],
        request.form['lastName'],
        request.form['email'],
        request.form['password'],
    )
    error = None

    if not user.first_name:
        error = 'Please enter your first name'
    elif not user.last_name:
        error = 'Please enter your last name'
    elif not user.email:
        error = 'Please enter your email'
    elif not user.password:
        error = 'Please choose a password'

    if error is None:
        user.password = generate_password_hash(user.password)
       
        try:       
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError: 
            error= "This email already exists"
        else:
            return redirect(url_for('show_login_form'))
    
    return error, 400

@app.post('/login')
def login():
    email= request.form['email']
    password= request.form['password']
    error= None

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

    if user is None:
        error = "incorrect email"
    elif not check_password_hash(user.password, password):
        error = "password don't match"

    if error is None:
        session["email"] = user.email
        # optional: flash a message
        flash('Logged in successfully')
        return redirect(url_for('index'))
    else:
        flash(error)
        return redirect(url_for('show_login_form'))


@app.route('/sign-up', methods=['GET'])
def show_sign_up_form():
    return render_template('sign-up.html')


@app.get('/login')
def show_login_form():
    return render_template('login.html')


@app.post('/create-post')
def create_post():
    caption = request.form['postCaption']
    error = None
    user = None
    
    if 'email' in session:
        user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one()
        post = Post(user.id, caption)
        db.session.add(post)
        db.session.commit()
    else:
        error = 'User not logged in'
 
    if error is None:
        return redirect(url_for('index'))
    else:
        return error, 401


@app.get('/profile')
def show_profile():
    if 'email' not in session:
        return redirect(url_for('show_login_form'))

    user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one()

    # compute avatar url (file-based avatar) and load user's posts for timeline
    avatar_url = get_avatar_url_for_user_id(user.id)
    posts = None
    try:
        posts = db.session.execute(db.select(Post).filter_by(user_id=user.id).order_by(Post.created_at.desc())).scalars().all()
    except Exception:
        posts = None

    return render_template('profile.html', current_user=user, avatar_url=avatar_url, posts=posts)


@app.get('/profile/edit')
def edit_profile_form():
    if 'email' not in session:
        return redirect(url_for('show_login_form'))

    user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one()
    return render_template('edit-profile.html', current_user=user)


@app.post('/profile/edit')
def edit_profile():
    if 'email' not in session:
        return redirect(url_for('show_login_form'))

    user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one()

    # Update simple fields
    first = request.form.get('firstName')
    last = request.form.get('lastName')
    dob = request.form.get('dateOfBirth')
    if first:
        user.first_name = first
    if last:
        user.last_name = last
    if dob:
        try:
            user.date_of_birth = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        except Exception:
            # ignore parse errors; could flash a message
            pass

    # No file uploads handled here (profile images removed to match DB schema).
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('show_profile'))


# Photo removal endpoint removed (images not supported without DB column).


@app.get('/api/post/<int:post_id>/like')
def like_post(post_id):
    """API: Increment likes for a post and return the new like count.

    Returns JSON: {"id": <post_id>, "likes": <new_count>} or 404 if not found.
    This endpoint uses GET to keep the frontend call simple (no CSRF handling shown
    elsewhere in the app). If you add authentication later, consider POST and CSRF.
    """
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar_one_or_none()
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    user = None
    if "email" in session:
        user = db.session.execute(db.select(User).filter_by(email=session["email"])).scalar_one()
    else:
        return jsonify({"error": "Log in to like a post"}), 404

    # Ensure likes is an int and increment
    new_like = Likes(user.id, post_id)
    db.session.add(new_like)
    db.session.commit()

    likes = db.session.execute(db.select(func.count()).select_from(Likes).filter_by(post_id=post.id)).scalar_one()

    return jsonify({"id": post.id, "likes": likes})


@app.route('/profile/avatar', methods=['POST'])
def upload_avatar():
    if 'email' not in session:
        flash("Please log in to upload an avatar.")
        return redirect(url_for('show_login_form'))

    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash('No file selected.')
        return redirect(url_for('show_profile'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Allowed: png, jpg, jpeg, gif')
        return redirect(url_for('show_profile'))

    user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one_or_none()
    if not user:
        flash('User not found.')
        return redirect(url_for('show_login_form'))

    # remove existing avatar files for this user
    pattern = os.path.join(AVATAR_FOLDER, f"user_{user.id}.*")
    for p in glob.glob(pattern):
        try:
            os.remove(p)
        except OSError:
            pass

    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    filename = f"user_{user.id}.{ext}"
    filepath = os.path.join(AVATAR_FOLDER, filename)
    file.save(filepath)
    flash('Avatar uploaded.')
    return redirect(url_for('show_profile'))


@app.route('/profile/avatar/remove', methods=['POST'])
def remove_avatar():
    if 'email' not in session:
        flash("Please log in to remove avatar.")
        return redirect(url_for('show_login_form'))

    user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one_or_none()
    if not user:
        flash('User not found.')
        return redirect(url_for('show_login_form'))

    pattern = os.path.join(AVATAR_FOLDER, f"user_{user.id}.*")
    removed = False
    for p in glob.glob(pattern):
        try:
            os.remove(p)
            removed = True
        except OSError:
            pass

    flash('Avatar removed.' if removed else 'No avatar to remove.')
    return redirect(url_for('show_profile'))


# Add server-side change-password endpoint
@app.post('/profile/change-password')
def change_password():
    if 'email' not in session:
        flash("Please log in to change your password.")
        return redirect(url_for('show_login_form'))

    user = db.session.execute(db.select(User).filter_by(email=session['email'])).scalar_one_or_none()
    if not user:
        flash("User not found.")
        return redirect(url_for('show_login_form'))

    current = request.form.get('currentPassword', '').strip()
    new = request.form.get('newPassword', '').strip()
    confirm = request.form.get('confirmPassword', '').strip()

    if not current or not new or not confirm:
        flash("All password fields are required.")
        return redirect(url_for('edit_profile_form'))

    if not check_password_hash(user.password, current):
        flash("Current password is incorrect.")
        return redirect(url_for('edit_profile_form'))

    if new != confirm:
        flash("New password and confirmation do not match.")
        return redirect(url_for('edit_profile_form'))

    if len(new) < 8:
        flash("New password must be at least 8 characters.")
        return redirect(url_for('edit_profile_form'))

    user.password = generate_password_hash(new)
    db.session.add(user)
    db.session.commit()

    flash("Password changed successfully.")
    return redirect(url_for('show_profile'))


# these lines indicates that we are in  "development mode"
# they will only execute if we run the app by executing this file directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
