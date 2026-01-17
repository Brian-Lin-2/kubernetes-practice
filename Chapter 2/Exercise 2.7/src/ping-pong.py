from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:secret@ping-db-svc:3002/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for storing the counter
class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

# Ensure the table exists
with app.app_context():
    db.create_all()
    # Initialize the counter if it doesn't exist
    if Counter.query.first() is None:
        db.session.add(Counter(count=0))
        db.session.commit()

@app.route("/pingpong")
def pingpong():
    counter = Counter.query.first()
    counter.count += 1
    db.session.commit()
    return f"Pong! Count: {counter.count}\n"

@app.route("/count")
def get_count():
    counter = Counter.query.first()
    return jsonify({"count": counter.count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


