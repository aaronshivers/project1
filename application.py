import os

from dotenv import load_dotenv
from flask import Flask, session, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
load_dotenv()

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
  url = "https://www.goodreads.com/book/review_counts.json"
  res = requests.get(url, params={"key": os.getenv('GOODREADS_KEY'), "isbns": "9781632168146"})
  json = res.json()
  return jsonify(json)
