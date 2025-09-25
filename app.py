from flask import Flask, render_template, url_for, redirect, flash, request
from flask_wtf import FlaskForm
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from wtforms import StringField, PasswordField, TextAreaField, EmailField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOU-WILL-NEVER-KNOW'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    location = db.Column(db.String(150))  
    bio = db.Column(db.Text, nullable=True)  # Optional bio
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

    # define relationship: A user can make many posts.
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    message = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
class SignUpForm(FlaskForm): 
    username = StringField('Username', render_kw={'placeholder': 'Please input name'}, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = EmailField('Email', validators=[Email(), DataRequired()])
    location = StringField('Location')  # New field
    bio = TextAreaField('Bio (Optional)')  # New field
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm): #Login page for existing users to log in 
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('title', 
                           render_kw={'placeholder': 'Please input title'}, 
                           validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])    
    submit = SubmitField('Create Post')

#Input Signup Page as Initial Page and block every other page until signing up is verified
@app.route('/')
def index():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_email:
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('signup'))
        
        if not existing_user:
            user = User(
                username=form.username.data,
                email=form.email.data,
                location=form.location.data,  # Handle location
                bio=form.bio.data  # Handle bio
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Sign Up successful!')
            return redirect(url_for('home'))
        else:
            flash('User already exists.')
    return render_template('signup.html', title='SignUp', form=form)



@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Update the user's bio
        bio = request.form.get('bio')
        current_user.bio = bio
        db.session.commit()
        flash('Bio updated successfully!', 'success')
        return redirect(url_for('home'))
    
    # Fetch posts by the current user
    current_user_posts = Post.query.filter_by(user_id=current_user.id).all()

    # Fetch all posts
    all_posts = Post.query.all()

    return render_template(
        'home.html',
        user=current_user,
        current_user_posts=current_user_posts,
        posts=all_posts
    )


# define another route
@app.route('/user')
@app.route('/user/<string:name>') # VS. @app.route('/user/name') 
@login_required
def user_home(name):
    user = User.query.filter_by(username=name).first_or_404()
    return render_template('home.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)



@app.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    message=form.message.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('createpost.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signup'))


if __name__ =='__main__': 
    app.run(debug=True)
# Additional Models

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class TripPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

class ProductReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(120), nullable=True)

# Additional Routes

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')
        if not email or not message:
            flash('Email and message are required!', 'error')
        else:
            inquiry = Inquiry(email=email, message=message)
            db.session.add(inquiry)
            db.session.commit()
            flash('Your inquiry has been submitted!', 'success')
            return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/trip_planner', methods=['GET', 'POST'])
@login_required
def trip_planner():
    if request.method == 'POST':
        location = request.form.get('location')
        date = request.form.get('date')
        budget = request.form.get('budget')
        duration = request.form.get('duration')
        if not location or not date or not budget or not duration:
            flash('All fields are required!', 'error')
        else:
            total_cost = float(budget) * int(duration)
            trip = TripPlan(user_id=current_user.id, location=location, date=date, budget=budget, duration=duration, total_cost=total_cost)
            db.session.add(trip)
            db.session.commit()
            flash(f'Trip planned to {location} on {date}. Total cost: ${total_cost:.2f}', 'success')
            return redirect(url_for('trip_planner'))
    return render_template('trip_planner.html')

# Utility
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviews():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        review = request.form.get('review')
        rating = request.form.get('rating')
        image = request.files.get('image')

        if not product_name or not review or not rating:
            flash('All fields are required!', 'error')
        elif int(rating) < 1 or int(rating) > 5:
            flash('Rating must be between 1 and 5!', 'error')
        elif image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_review = ProductReview(
                product_name=product_name,
                review=review,
                rating=int(rating),
                image_filename=filename
            )
            db.session.add(new_review)
            db.session.commit()
            flash('Review submitted successfully!', 'success')
        else:
            flash('Invalid file type for the image.', 'error')

    reviews = ProductReview.query.all()
    return render_template('reviews.html', reviews=reviews)
