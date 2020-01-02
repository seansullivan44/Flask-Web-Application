from flask import render_template, url_for, flash, redirect, request, abort
from FlaskApplication import app, db, bcrypt
from FlaskApplication.forms import RegestrationForm, LoginForm, UpdateAccountForm, PostForm
from FlaskApplication.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

#Home Page
@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    newestPosts = posts[-4:]
    return render_template('home.html', posts=posts, newestPosts=newestPosts)

#About Page
@app.route("/about")
def about():
    posts = Post.query.all()
    newestPosts = posts[-4:]
    return render_template('about.html',title=about,newestPosts=newestPosts)


#Register For New Account Page
@app.route("/register", methods=["GET","POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    regestrationForm = RegestrationForm()
    if regestrationForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(regestrationForm.password.data).decode("utf-8")
        user = User(username=regestrationForm.username.data, email=regestrationForm.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {regestrationForm.username.data}!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html',title='Register', form=regestrationForm)

#Login To Account Page
@app.route("/login", methods=["GET","POST"])
def login():

    if current_user.is_authenticated:
        flash("Already logged in")
        return redirect(url_for("home"))


    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
            login_user(user, remember=loginForm.remember.data)
            next_page = request.args.get("next")
            flash("You have logged in!",'success')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful!")
    return render_template('login.html',title='Login', form=loginForm)


#Logout Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

#Function to Take User Picture, Modify it's Size, Save it and Return FileName
def savePicture(formPicture):
    random_hex = secrets.token_hex(32)
    fileName, fileExt = os.path.splitext(formPicture.filename)
    pictureFileName = random_hex + fileExt
    picturePath = os.path.join(app.root_path, "static/profile_pictures", pictureFileName)
    outputSize = (125,125)
    i = Image.open(formPicture)
    i.thumbnail(outputSize)
    i.save(picturePath)
    return pictureFileName


#User Account Page
@app.route("/account", methods=["GET","POST"])
@login_required
def account():
    updateAccountForm = UpdateAccountForm()
    if updateAccountForm.validate_on_submit():
        if updateAccountForm.profilePicture.data:
            pictureFile = savePicture(updateAccountForm.profilePicture.data)
            current_user.imageFile = pictureFile

        current_user.username = updateAccountForm.username.data
        current_user.email = updateAccountForm.email.data
        db.session.commit()
        flash(current_user.username+"'s account has been updated!","success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        updateAccountForm.username.data = current_user.username
        updateAccountForm.email.data = current_user.email

    posts = Post.query.all()
    newestPosts = posts[-4:]

    imageFile = url_for('static', filename="profile_pictures/"+current_user.imageFile)
    return render_template('account.html',title='Account', imageFile = imageFile, form=updateAccountForm, newestPosts=newestPosts)

#Create New Post Page
@app.route("/post/new", methods=["GET","POST"])
@login_required
def newPost():
    postForm = PostForm()
    if postForm.validate_on_submit():
        post = Post(title=postForm.title.data,content=postForm.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('createPost.html',title='New Post',form=postForm, legend="New Post")

#Look at Specific Post
@app.route("/post/<int:post_id>")
def post(post_id):
    posts = Post.query.all()
    newestPosts = posts[-4:]
    post = Post.query.get_or_404(post_id)
    return render_template("posts.html", title=post.title, post=post,newestPosts=newestPosts)

#Update a Specific Post
@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def updatePost(post_id):
    posts = Post.query.all()
    newestPosts = posts[-4:]
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated")
        return redirect(url_for("post",post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('createPost.html',title='Update Post',form=form, legend="Update Post", newestPosts=newestPosts)

#Delete a Specific
@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def deletePost(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your Post Has Been Deleted")
    return redirect(url_for("home"))
