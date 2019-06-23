import os

from dotenv import load_dotenv
from flask import Flask, session, jsonify, request, redirect, make_response, after_this_request
from flask_talisman import Talisman
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_marshmallow import Marshmallow
import requests

app = Flask(__name__)
Talisman(app)
# load_dotenv()

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

# User Model
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  password = db.Column(db.String(100), nullable=False)

  def __init__(self, name, password):
    self.name = name
    self.password = password

# User Schema
class UserSchema(ma.Schema):
  class Meta:
    # Fields to Expose
    fields = ('id', 'name', 'password')

# Initialize User Schema
user_schema = UserSchema(strict=True)
users_schema = UserSchema(many=True, strict=True)

@app.route("/")
def index():
  url = "https://www.goodreads.com/book/review_counts.json"
  res = requests.get(url, params={"key": os.getenv('GOODREADS_KEY'), "isbns": "9781632168146"})
  json = res.json()
  return jsonify(json)

@app.route('/users', methods=['POST', 'GET'])
def users():
  if request.method == 'POST':
    name = request.json['name']
    password = request.json['password']
    new_user = User(name, password)

    try:
      db.session.add(new_user)
      db.session.commit()
      return user_schema.jsonify(new_user)

    except:
      return 'The user could not be added.'

  else:
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)

@app.route('/secret')
def secret():
  name = request.cookies.get('is_logged_in')
  return '<h1>welcome to the secret page</h1>'

@app.route('/test')
def test():
  @after_this_request
  def add_header(response):
    response.headers['x-auth-token'] = 'hey there'
    return response
  return 'test successful'

@app.route('/login', methods=['POST'])
def login():

  name = request.json['name']
  password = request.json['password']

  try:
    user = User.query.filter_by(name=name).first()

    if user.name == name and user.password == password:
      return redirect('/')

    else:
      return 'Invalid Login'

  except:
    return 'Invalid Login'
