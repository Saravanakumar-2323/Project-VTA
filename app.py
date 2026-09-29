import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'my_super_secret_lms_key_123'  # Secret key for Session & Flash

# ==================== CONFIGURATIONS ====================
# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploaded_files'

# Gmail SMTP Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'saravanakumar23133@gmail.com'
app.config['MAIL_PASSWORD'] = 'pvvy uetj beur poyo'  # App Password

db = SQLAlchemy(app)
mail = Mail(app)

# ==================== DATABASE MODELS ====================

# 1. User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='student')
    image = db.Column(db.String(100), default='pic-1.jpg')
    
    # Personal & Extra Details Fields (Optional)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.String(30), nullable=True)
    school = db.Column(db.String(150), nullable=True)
    college = db.Column(db.String(150), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    github = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    other_social = db.Column(db.Text, nullable=True)  # Multiple social links stored as CSV
    
    # Relationships
    courses = db.relationship('Course', backref='tutor', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)

# 2. Course / Playlist Model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumb = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    videos = db.relationship('Video', backref='course', lazy=True, cascade="all, delete-orphan")
    bookmarks = db.relationship('Bookmark', backref='course', lazy=True, cascade="all, delete-orphan")

# 3. Video Model
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    video_file = db.Column(db.String(100), nullable=False)
    thumb = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='video', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='video', lazy=True, cascade="all, delete-orphan")

# 4. Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

# 5. Like Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

# 6. Bookmark Model
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# 7. Contact Model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ==================== PUBLIC & USER ROUTES ====================
@app.route('/')
def home():
    courses = Course.query.limit(6).all()
    
    # Guest metrics
    total_courses = Course.query.count()
    total_tutors = User.query.filter(User.courses.any()).count()
    
    try:
        total_likes = Like.query.count()
    except Exception:
        total_likes = 0

    user_enrolled = 0
    user_likes = 0
    user_discussions = 0
    user_saved = 0
    tutor_courses = 0
    total_students = 0

    if 'user_id' in session:
        user_id = session['user_id']
        current_role = session.get('user_role') or session.get('role')
        
        if current_role == 'tutor':
            tutor_courses = Course.query.filter_by(user_id=user_id).count()
        else:
            user_enrolled = 0

        try:
            user_likes = Like.query.filter_by(user_id=user_id).count()
            user_discussions = Comment.query.filter_by(user_id=user_id).count()
            user_saved = Bookmark.query.filter_by(user_id=user_id).count()
        except Exception:
            pass

    return render_template(
        'home.html',
        courses=courses,
        total_courses=total_courses,
        total_tutors=total_tutors,
        total_likes=total_likes,
        user_enrolled=user_enrolled,
        user_likes=user_likes,
        user_discussions=user_discussions,
        user_saved=user_saved,
        tutor_courses=tutor_courses,
        total_students=total_students
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/teachers')
def teachers():
    tutors = User.query.filter(User.courses.any()).all()
    return render_template('teachers.html', tutors=tutors)

@app.route('/tutor/<int:tutor_id>')
def tutor_profile(tutor_id):
    tutor = User.query.get_or_404(tutor_id)
    courses = Course.query.filter_by(user_id=tutor_id).all()
    return render_template('tutor_profile.html', tutor=tutor, courses=courses)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('number')
        user_msg = request.form.get('msg')

        new_contact = Contact(name=name, email=email, number=number, message=user_msg)
        db.session.add(new_contact)
        db.session.commit()

        msg = Message(
            subject=f"New LMS Contact Message from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=['saravanakumar23133@gmail.com'],
            body=f"Name: {name}\nEmail: {email}\nPhone: {number}\n\nMessage:\n{user_msg}"
        )
        
        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'Message saved in DB, but email failed: {e}', 'warning')

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/playlist/<int:course_id>')
def playlist(course_id):
    course = Course.query.get_or_404(course_id)
    videos = Video.query.filter_by(course_id=course.id).all()
    
    is_bookmarked = False
    if 'user_id' in session:
        is_bookmarked = Bookmark.query.filter_by(
            user_id=session['user_id'], 
            course_id=course.id
        ).first() is not None

    return render_template('playlist.html', course=course, videos=videos, is_bookmarked=is_bookmarked)

@app.route('/bookmarks')
def bookmarks():
    if 'user_id' not in session:
        flash('Please login to view saved playlists!', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user_bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    courses = [b.course for b in user_bookmarks] if user_bookmarks else []
    return render_template('bookmark.html', courses=courses)

@app.route('/bookmark/<int:course_id>', methods=['POST'])
def bookmark_course(course_id):
    if 'user_id' not in session:
        flash('Please login to save playlists!', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    existing_bookmark = Bookmark.query.filter_by(user_id=user_id, course_id=course_id).first()

    if existing_bookmark:
        db.session.delete(existing_bookmark)
        db.session.commit()
        flash('Playlist removed from bookmarks!', 'info')
    else:
        new_bookmark = Bookmark(user_id=user_id, course_id=course_id)
        db.session.add(new_bookmark)
        db.session.commit()
        flash('Playlist saved successfully!', 'success')

    return redirect(url_for('playlist', course_id=course_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('pass')
        c_password = request.form.get('c_pass')
        role = request.form.get('role', 'student')  
        image_file = request.files.get('image')

        if password != c_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This Email is already registered!', 'error')
            return redirect(url_for('register'))

        filename = 'pic-1.jpg'
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        hashed_password = generate_password_hash(password)

        new_user = User(name=name, email=email, password=hashed_password, image=filename, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_image'] = user.image
            session['user_role'] = user.role
            session['role'] = user.role
            return redirect(url_for('home'))
        else:
            flash('Invalid Email or Password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile!', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    saved_count = Bookmark.query.filter_by(user_id=user_id).count()
    likes_count = Like.query.filter_by(user_id=user_id).count()
    comments_count = Comment.query.filter_by(user_id=user_id).count()
    
    return render_template(
        'profile.html', 
        user=user, 
        saved_count=saved_count, 
        likes_count=likes_count, 
        comments_count=comments_count
    )

@app.route('/update', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        flash('Please login to update your profile!', 'warning')
        return redirect(url_for('login'))
        
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        old_pass = request.form.get('old_pass')
        new_pass = request.form.get('new_pass')
        c_pass = request.form.get('c_pass')
        image_file = request.files.get('image')

        # Personal & Educational Details
        user.gender = request.form.get('gender')
        user.dob = request.form.get('dob')
        user.school = request.form.get('school')
        user.college = request.form.get('college')
        user.bio = request.form.get('bio')
        user.linkedin = request.form.get('linkedin')
        user.github = request.form.get('github')
        user.website = request.form.get('website')
        
        # Multiple social links logic
        other_links = request.form.getlist('other_social[]')
        valid_links = [link.strip() for link in other_links if link.strip()]
        user.other_social = ",".join(valid_links) if valid_links else None

        if name:
            user.name = name
            session['user_name'] = name
        if email:
            user.email = email
            session['user_email'] = email

        if old_pass or new_pass:
            if not check_password_hash(user.password, old_pass):
                flash('Old password is incorrect!', 'error')
                return redirect(url_for('update_profile'))
            if new_pass != c_pass:
                flash('New passwords do not match!', 'error')
                return redirect(url_for('update_profile'))
            user.password = generate_password_hash(new_pass)

        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.image = filename
            session['user_image'] = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('update.html', user=user)

@app.route('/watch-video/<int:video_id>', methods=['GET', 'POST'])
def watch_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Please login to like or comment!', 'warning')
            return redirect(url_for('login'))

        if 'like_btn' in request.form:
            existing_like = Like.query.filter_by(user_id=session['user_id'], video_id=video.id).first()
            if existing_like:
                db.session.delete(existing_like)
                db.session.commit()
                flash('Unliked video!', 'info')
            else:
                new_like = Like(user_id=session['user_id'], video_id=video.id)
                db.session.add(new_like)
                db.session.commit()
                flash('Liked video!', 'success')
            return redirect(url_for('watch_video', video_id=video.id))

        if 'add_comment' in request.form:
            comment_input = request.form.get('comment_box')
            if comment_input:
                new_comment = Comment(
                    comment_text=comment_input,
                    user_id=session['user_id'],
                    video_id=video.id
                )
                db.session.add(new_comment)
                db.session.commit()
                flash('Comment added successfully!', 'success')
                return redirect(url_for('watch_video', video_id=video.id))

    likes_count = Like.query.filter_by(video_id=video.id).count()
    user_liked = False
    if 'user_id' in session:
        user_liked = Like.query.filter_by(user_id=session['user_id'], video_id=video.id).first() is not None

    return render_template('watch-video.html', video=video, likes_count=likes_count, user_liked=user_liked)

@app.route('/search', methods=['GET', 'POST'])
def search_course():
    query = request.args.get('query', '').strip()
    
    if query:
        search_pattern = f"%{query}%"
        courses = Course.query.join(User).filter(
            (Course.title.ilike(search_pattern)) | 
            (Course.description.ilike(search_pattern)) |
            (User.name.ilike(search_pattern))
        ).all()
    else:
        courses = Course.query.all()
        
    return render_template('courses.html', courses=courses, query=query)

# ==================== TEACHER / ADMIN DASHBOARD ROUTES ====================

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session:
        flash('Please login to access Teacher Dashboard!', 'warning')
        return redirect(url_for('login'))
    
    tutor_courses = Course.query.filter_by(user_id=session['user_id']).all()
    return render_template('teacher_dashboard.html', courses=tutor_courses)

@app.route('/teacher/add-course', methods=['GET', 'POST'])
def add_course():
    if 'user_id' not in session:
        flash('Please login to create a course!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        thumb_file = request.files.get('thumb')

        filename = 'thumb-1.png'
        if thumb_file and thumb_file.filename != '':
            filename = secure_filename(thumb_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            thumb_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_course = Course(
            title=title,
            description=description,
            thumb=filename,
            user_id=session['user_id']
        )
        db.session.add(new_course)
        db.session.commit()

        flash('New Course created successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))

    return render_template('add_course.html')

@app.route('/teacher/add-video/<int:course_id>', methods=['GET', 'POST'])
def add_video(course_id):
    if 'user_id' not in session:
        flash('Please login to upload videos!', 'warning')
        return redirect(url_for('login'))

    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        title = request.form.get('title')
        thumb_file = request.files.get('thumb')
        video_file = request.files.get('video')

        thumb_name = 'post-1-1.png'
        if thumb_file and thumb_file.filename != '':
            thumb_name = secure_filename(thumb_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            thumb_file.save(os.path.join(app.config['UPLOAD_FOLDER'], thumb_name))

        video_name = 'vid-1.mp4'
        if video_file and video_file.filename != '':
            video_name = secure_filename(video_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_name))

        new_video = Video(
            title=title,
            thumb=thumb_name,
            video_file=video_name,
            course_id=course.id
        )
        db.session.add(new_video)
        db.session.commit()

        flash('Video added to course successfully!', 'success')
        return redirect(url_for('playlist', course_id=course.id))

    return render_template('add_video.html', course=course)

# Single Fix Schema Route (adds missing columns without crashing)
@app.route('/fix-db-schema')
def fix_db_schema():
    columns = [
        "role VARCHAR(20) DEFAULT 'student'",
        "gender VARCHAR(20)",
        "dob VARCHAR(30)",
        "school VARCHAR(150)",
        "college VARCHAR(150)",
        "bio TEXT",
        "linkedin VARCHAR(200)",
        "github VARCHAR(200)",
        "website VARCHAR(200)",
        "other_social TEXT"
    ]
    
    for col in columns:
        try:
            db.session.execute(db.text(f"ALTER TABLE user ADD COLUMN {col};"))
            db.session.commit()
        except Exception:
            db.session.rollback()
            
    return "All missing columns added successfully to User table!"

if __name__ == '__main__':
    app.run(debug=True)