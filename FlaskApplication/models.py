from datetime import datetime
from FlaskApplication import db, loginManager
from flask_login import UserMixin

#Manage Multiple User Login
@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Model of a User Account To Be Stored In Database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imageFile = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #Posts that the user has created:
    posts = db.relationship('Post',backref='author', lazy=True)


#Model of a User Post To Be Stored In Database
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    datePosted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    #Link post to a user in the users table:
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
