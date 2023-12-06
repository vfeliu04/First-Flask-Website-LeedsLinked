"""Import necessary libraries"""
import json
from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, or_
from app.models import User, Posts
from app import app, db
from .forms import RegisterForm, LoginForm, PostForm, UpdateUser, SearchForm

# Flask_LogIn Definitions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# FlaskAdmin Definitions
admin = Admin()
admin.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Function to load a user by ID for Flask Login"""
    return User.query.get(int(user_id))


class UserAdmin(ModelView):
    """Admin Views for User"""
    column_list = ('id', 'username', 'password_hash', 'name', 'age',
                   'nationality', 'email', 'relationship_status',
                   'student_bio', 'major', 'year_of_study', 'birthdate',
                   'linkedIn', 'instagram', 'snapchat', 'viewd', 'blogs_created')


class PostsAdmin(ModelView):
    """Admin Views for Post"""
    column_list = ('id', 'title', 'content', 'date_posted',
                   'slug', 'blogger_id', 'likes', 'dislikes')


admin.add_view(UserAdmin(User, db.session))
admin.add_view(PostsAdmin(Posts, db.session))


@app.context_processor
def base():
    """Context processor to add a SearchForm instance to the base context"""
    form = SearchForm()
    return dict(form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Function to register user"""
    with app.app_context():
        # Bfore register make sure that the user is logged out
        logout_user()
        form = RegisterForm()
        if form.validate_on_submit():
            username_repeated = User.query.filter_by(
                username=form.username.data).first()
            email_repeated = User.query.filter_by(email=form.email.data).first()
            # Check that username nor email is repeated and passwords match
            if (username_repeated is None) and (email_repeated is
                                                None) and (form.password_hash.data ==
                                                           form.password_hash2.data):
                user = User(username=form.username.data,
                                    name=form.name.data, email=form.email.data,
                                    password_hash=generate_password_hash(form.password_hash.data,
                                                                         "pbkdf2:sha256"))
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("Registered!!")
                return redirect(url_for('home'))
            else:
                if form.password_hash.data != form.password_hash2.data:
                    flash("Passwords do not match")
                else:
                    flash("Account already exits!")
    return render_template('register.html', form=form)


@app.route('/search', methods=['POST'])
@login_required
def search():
    """Function to search blog"""
    form = SearchForm()
    all_posts = Posts.query
    if form.is_submitted():
        # If user searches nothing
        if len(form.searched.data) == 0:
            print(form.searched.data)
            flash("Missing Data!")
            return redirect(url_for('posts'))
        else:
            # Get posts that include the search in the title, content, blog_creator or slug
            all_posts = all_posts.filter(
                or_(
                    Posts.content.like(f'%{form.searched.data}%'),
                    Posts.title.like(f'%{form.searched.data}%'),
                    Posts.blog_creator.has(
                        User.name.like(f'%{form.searched.data}%')),
                    Posts.slug.like(f'%{form.searched.data}%')
                )
            )
            all_posts = all_posts.order_by(Posts.title).all()
            return render_template('search.html', form=form, all_posts=all_posts,
                                   searched=form.searched.data)


@app.route('/')
def home():
    """Function for home page"""
    return render_template('home.html')


@app.route('/my_blogs')
@login_required
def my_blogs():
    """Function user's blog page"""
    all_posts = Posts.query.filter_by(blogger_id=current_user.id).order_by(
        desc(Posts.date_posted)).all()
    return render_template('myBlogs.html', all_posts=all_posts)


@app.route('/addBlog', methods=['GET', 'POST'])
@login_required
def add_post():
    """Function to add blog"""
    with app.app_context():
        form = PostForm()
        blogger = current_user.id
        if form.validate_on_submit():
            post = Posts(title=form.title.data, content=form.content.data,
                         slug=form.slug.data, blogger_id=blogger)
            db.session.add(post)
            db.session.commit()
            flash("Blog Post Submitted Successfully")
            return redirect(url_for('my_blogs'))
        return render_template('addBlog.html', form=form)


@app.route('/blogPosts')
@login_required
def posts():
    """Function to show all blogs"""
    all_posts = Posts.query.all()
    # Calculate the score of the posts when the function is called
    for post in all_posts:
        post.calculate_score()
    # Order posts by the score calculated
    all_posts = Posts.query.order_by(desc(Posts.score)).all()
    user_posts = Posts.query.filter_by(
        blogger_id=current_user.id).order_by(desc(Posts.date_posted)).all()
    return render_template('blogPosts.html', posts=all_posts, user_posts=user_posts)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def single_post(id):
    """Function to show single blog post"""
    with app.app_context():
        current_post = Posts.query.get_or_404(id)
        # If the current user is the blog creator don't add him to the viewer list
        if current_post.blogger_id != current_user.id:
            current_post.viewers.append(current_user)
        like_count = len(current_post.likes)
        dislike_count = len(current_post.dislikes)
        db.session.commit()
        # Only show the last 10 (or less than 10) users who viewed the blog
        if len(current_post.viewers) >= 10:
            recent_views = current_post.viewers[-10:]
            recent_views.reverse()
        else:
            recent_views = current_post.viewers
            recent_views.reverse()
        return render_template('post.html', post=current_post, current_user=current_user,
                               recent_views=recent_views,
                               like_count=like_count, dislike_count=dislike_count)


@app.route('/likes', methods=['POST'])
def likes():
    """Function to like blog post"""
    with app.app_context():
        # Load the JSON data and use the ID of the idea that was clicked to get the object
        data = json.loads(request.data)
        post_id = int(data.get('post_id'))
        user_id = int(data.get('user_id'))

        user = User.query.get(user_id)
        post = Posts.query.get(post_id)

        if user and post:
            # If user has not liked the post
            if (user not in post.likes) and (user not in post.dislikes):
                if data.get('like_type') == "like":
                    post.likes.append(user)
                else:
                    post.dislikes.append(user)
                db.session.commit()
                return json.dumps({'status': 'OK', 'like':
                    len(post.likes), 'dislike': len(post.dislikes)})
            # If user has liked the post
            elif (user in post.likes) and (data.get('like_type') == "like"):
                post.likes.remove(user)
                db.session.commit()
                return json.dumps({'status': 'OK', 'like':
                    len(post.likes), 'dislike': len(post.dislikes)})
            # If user has disliked the post
            elif (user in post.dislikes) and (data.get('like_type') != "like"):
                post.dislikes.remove(user)
                db.session.commit()
                return json.dumps({'status': 'OK', 'like':
                    len(post.likes), 'dislike': len(post.dislikes)})
            # If user has disliked the post but has already liked
            elif (user in post.likes) and (data.get('like_type') != "like"):
                post.likes.remove(user)
                post.dislikes.append(user)
                db.session.commit()
                return json.dumps({'status': 'OK', 'like':
                    len(post.likes), 'dislike': len(post.dislikes)})
            else:
                post.likes.append(user)
                post.dislikes.remove(user)
                db.session.commit()
                return json.dumps({'status': 'OK', 'like':
                    len(post.likes), 'dislike': len(post.dislikes)})


@app.route('/post_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """Function to edit post"""
    with app.app_context():
        form = PostForm()
        post = Posts.query.get_or_404(id)
        # Double check that the current user is the author of the blog
        if current_user.id == post.blog_creator.id:
            if form.validate_on_submit():
                post.title = form.title.data
                post.slug = form.slug.data
                post.content = form.content.data
                db.session.add(post)
                db.session.commit()
                flash("Blog Post Edited Successfully")
                return redirect(url_for('posts'))
            # Populate the form with the existing data
            form.title.data = post.title
            form.slug.data = post.slug
            form.content.data = post.content
            return render_template('editPost.html', form=form)
        else:
            flash("Sorry you can't edit this post")
            return redirect(request.referrer or url_for('default_route'))


@app.route('/post_delete/<int:id>')
@login_required
def delete_post(id):
    """Function to delete post"""
    with app.app_context():
        post_to_delete = Posts.query.get_or_404(id)
        # Check that the current user is the author of the post to delete
        if current_user.id == post_to_delete.blog_creator.id:
            # Try to delete the post
            try:
                db.session.delete(post_to_delete)
                db.session.commit()
                flash("Post Deleted!!")
                return redirect(request.referrer or url_for('default_route'))
            except:
                flash("Can't delete that post!!")
                return redirect(request.referrer or url_for('default_route'))
        else:
            flash("Sorry you can't delete this post")
            return redirect(request.referrer or url_for('default_route'))


@app.route('/profile')
@login_required
def profile():
    """Function to show user profile"""
    name = current_user.name
    email = current_user.email
    age = current_user.age
    relationship_status = current_user.relationship_status
    major = current_user.major
    student_bio = current_user.student_bio
    nationality = current_user.nationality
    year_of_study = current_user.year_of_study
    birthdate = current_user.birthdate
    linkedIn = current_user.linkedIn
    instagram = current_user.instagram
    snapchat = current_user.snapchat
    blog_created_count = len(current_user.blogs_created)
    blog_read_count = len(current_user.viewd)
    # Show the last 3 (or less) posts that the user has viewed
    if len(current_user.viewd) >= 3:
        recent_blogs = current_user.viewd[-3:]
        recent_blogs.reverse()
    else:
        recent_blogs = current_user.viewd
        recent_blogs.reverse()
    return render_template('profile.html', name=name, email=email, age=age,
                           relationship_status=relationship_status,
                           student_bio=student_bio, major=major, year_of_study=year_of_study,
                           birthdate=birthdate, linkedIn=linkedIn, instagram=instagram,
                           snapchat=snapchat, blog_created_count=blog_created_count,
                           nationality=nationality,
                           blog_read_count=blog_read_count, recent_blogs=recent_blogs)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def view_other_profile(id):
    """Function to view other user profile"""
    with app.app_context():
        current_user_id = current_user.id
        user = User.query.get_or_404(id)
        user_id = user.id
        name = user.name
        email = user.email
        age = user.age
        relationship_status = user.relationship_status
        major = user.major
        student_bio = user.student_bio
        nationality = user.nationality
        year_of_study = user.year_of_study
        birthdate = user.birthdate
        linkedIn = user.linkedIn
        instagram = user.instagram
        snapchat = user.snapchat
        blog_created_count = len(user.blogs_created)
        blog_read_count = len(user.viewd)
        # Show the last 3 (or less) posts that the user has viewed
        if len(user.viewd) >= 3:
            recent_blogs = user.viewd[-3:]
            recent_blogs.reverse()
        else:
            recent_blogs = user.viewd
            recent_blogs.reverse()
        return render_template('profile.html', name=name, email=email, age=age,
                               relationship_status=relationship_status,
                               student_bio=student_bio, major=major, year_of_study=year_of_study,
                               birthdate=birthdate, linkedIn=linkedIn, instagram=instagram,
                               snapchat=snapchat, blog_created_count=blog_created_count,
                               nationality=nationality,
                               blog_read_count=blog_read_count, recent_blogs=recent_blogs,
                               current_user_id=current_user_id, user_id=user_id)


@app.route('/profile_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    """Function to edit user profile"""
    with app.app_context():
        # Make sure that it is the current user who can edit his own profile
        if id == current_user.id:
            form = UpdateUser()
            user = User.query.get_or_404(id)
            if form.validate_on_submit():
                user.username = form.username.data
                user.name = form.name.data
                user.email = form.email.data
                user.age = form.age.data
                user.relationship_status = form.relationship_status.data
                user.major = form.major.data
                user.nationality = form.nationality.data
                user.student_bio = form.student_bio.data
                user.year_of_study = form.year_of_study.data
                user.birthdate = form.birthdate.data
                user.linkedIn = form.linkedIn.data
                user.snapchat = form.snapchat.data
                user.instagram = form.instagram.data
                db.session.add(user)
                db.session.commit()
                flash("Profile Edited Successfully")
                return redirect(url_for('profile'))
            # Populate the form with the existing data
            form.username.data = user.username
            form.name.data = user.name
            form.email.data = user.email
            form.age.data = user.age
            form.relationship_status.data = user.relationship_status
            form.major.data = user.major
            form.student_bio.data = user.student_bio
            form.year_of_study.data = user.year_of_study
            form.birthdate.data = user.birthdate
            form.linkedIn.data = user.linkedIn
            form.snapchat.data = user.snapchat
            form.nationality.data = user.nationality
            form.instagram.data = user.instagram
            return render_template('editProfile.html', form=form)
        else:
            flash("Sorry, you can't edit that user! ")
            return redirect(url_for('profile'))


@app.route('/profile_delete/<int:id>')
@login_required
def delete_profile(id):
    """Function to delete user profile"""
    with app.app_context():
        # Make sure that the current user is the one who is deleting his profile
        if id == current_user.id:
            user_to_delete = User.query.get_or_404(id)
            all_posts = Posts.query.filter_by(blogger_id=current_user.id).all()
            # Try to delete profile
            try:
                db.session.delete(user_to_delete)
                db.session.commit()
                for post in all_posts:
                    db.session.delete(post)
                db.session.commit()
                flash("User Deleted Successfully!!")
                return redirect(url_for('login'))
            except:
                flash("Whoops! There was a problem deleting user, try again...")
                return redirect(url_for('profile'))
        else:
            flash("Sorry, you can't delete that user! ")
            return redirect(url_for('profile'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Function to login user"""
    logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("You are logged in!!")
                return redirect(url_for('home'))
            else:
                flash("Password Is Incorrect")
        else:
            flash("That email is not registered")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Function to logout user"""
    logout_user()
    flash("You have logged out")
    return redirect(url_for('home'))
