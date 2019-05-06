import os
from flask import Flask, redirect, url_for, jsonify, request
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_marshmallow import Marshmallow
import jwt
from functools import wraps

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissupposedtobesecret'
# DATABASE INITITAL
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

app.config["FACEBOOK_OAUTH_CLIENT_ID"] = "472717633470175"
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = "c209f953d18ee26f1deeb9d8e234622c"
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("892442284955-66p4eln67in1pm6h9hhd0e804gdcrgpb.apps.googleusercontent.com")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("Dq55Z9CZTnmxg-Qram0EpMOi")

facebook_bp = make_facebook_blueprint(
    scope='email',
    redirect_url = '/facebook'
)
app.register_blueprint(facebook_bp, url_prefix="/login")

google_bp = make_google_blueprint(
    client_id="892442284955-66p4eln67in1pm6h9hhd0e804gdcrgpb.apps.googleusercontent.com",
    client_secret="Dq55Z9CZTnmxg-Qram0EpMOi",
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_url = '/google'
)
app.register_blueprint(google_bp, url_prefix="/login")


class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column('id', db.Integer, primary_key = True)
    title = db.Column(db.String(200))

    def __init__(self, title):
        self.title = title

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique=True)
    full_name = db.Column(db.String(200))
    tel_no = db.Column(db.String(20))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    account_type = db.Column(db.String(10))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, email, full_name, job_id, account_type):
        self.email = email
        self.full_name = full_name
        self.job_id = job_id
        self.account_type = account_type
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return {'email': payload['email'], 'user_id': payload['user_id'], 'user_name': payload['user_name']}
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
    
    def encode_auth_token(self):
        token = jwt.encode({'email': self.email, 'user_name':self.full_name, 'user_id': self.id, 'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, app.config.get('SECRET_KEY'))
        return token.decode('UTF-8')

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    
    def __init__(self, title, content, owner_id):
        self.title = title
        self.content = content
        self.owner_id = owner_id
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

class PostSchema(ma.Schema):
    class Meta:
        fields = ['id', 'title', 'content', 'owner_id']

post_schema = PostSchema(strict=True)
posts_schema = PostSchema(many=True, strict=True)

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column('id', db.Integer, primary_key = True)
    user_name = db.Column(db.String(200))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, user_name, post_id, user_id):
        self.user_name = user_name
        self.post_id = post_id
        self.user_id = user_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

db.create_all()

@app.route('/facebook')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    account_info = facebook.get('/me?fields=id,email,name')

    if account_info.ok:
        account_info_json = account_info.json()
        user_info = {'name': account_info_json['name'], 'email': account_info_json['email']}
        user = User.query.filter(User.email == account_info_json['email']).first()
        print(user)
        if not user:
            user = User(email= account_info_json['email'],full_name=account_info_json['name'], job_id=None, account_type='Facebook')
            user.save()
        token = user.encode_auth_token()
        return jsonify({'token': token })

    return jsonify({'message': 'Resigter facebook failed'})

@app.route("/google")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    account_info = google.get("/oauth2/v2/userinfo")
    if account_info.ok:
        account_info_json = account_info.json()
        user_info = {'email': account_info_json['email']}

        user = User.query.filter(User.email == account_info_json['email']).first()
        if not user:
            user = User(email= account_info_json['email'],full_name=None, job_id=None, account_type='Google')
            user.save()
        token = user.encode_auth_token()
        return jsonify({'token': token })

    return jsonify({'message': 'Resigter google failed'})

def token_require(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'Token mission!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user_id = User.decode_auth_token(token)['user_id']
            user = User.query.get(user_id)
            print(user)

            if not user.full_name:
                return jsonify({'message': 'Please fill information!'}), 403    
        except:
            return jsonify({'message': 'Token invalid!'}), 403

        return f(*args, **kwargs)

    return decorated
    
@app.route("/post", methods=['GET'])
@token_require
def get_all_post():
    all_posts = Post.query.all()
    result = posts_schema.dump(all_posts)
    return jsonify(result.data)

@app.route("/post", methods=['POST'])
@token_require
def save_post():
    title = request.json['title']
    content = request.json['content']
    token = request.headers.get('token')
    owner_id = User.decode_auth_token(token)['user_id']

    post = Post(title=title, content = content, owner_id = owner_id)
    post.save()
    return jsonify(post_schema.dump(post).data)

@app.route("/post/<id>", methods=['GET'])
@token_require
def get_post(id):
    post = Post.query.get(id)
    return post_schema.jsonify(post)

@app.route("/own-post", methods=['GET'])
@token_require
def get_own_post():
    token = request.headers.get('token')
    user_id = User.decode_auth_token(token)['user_id']
    posts = Post.query.filter(Post.owner_id == user_id).all()
    result = posts_schema.dump(posts)
    return jsonify(result.data)

@app.route("/likes", methods=['POST'])
@token_require
def like():
    post_id = request.json['post_id']
    user_id = User.decode_auth_token(request.header.get('token'))['user_id']
    username = User.decode_auth_token(request.header.get('token'))['user_name']

    like = Like(user_name = username, post_id=post_id, user_id = user_id)
    like.save()
    return jsonify(like)

if __name__ == '__main__':
    app.run(debug=True)