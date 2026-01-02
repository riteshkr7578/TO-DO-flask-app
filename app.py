from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Good practice to suppress warnings
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

# --- DATABASE INITIALIZATION ---
# This ensures the .db file and tables are created on Render
with app.app_context():
    db.create_all()

# Added "HEAD" to methods to stop Render's health check from failing (405)
@app.route("/", methods=["GET", "POST", "HEAD"])
def bootstrap():
    if request.method == "HEAD":
        return "", 200  # Return empty success for health checks

    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")

        if title and desc:  
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
            return redirect("/") # Redirect after POST to prevent resubmission

    allTodo = Todo.query.all()
    return render_template("index.html", allTodo=allTodo)

@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        db.session.commit()
        return redirect("/")
    return render_template("update.html", todo=todo)

@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)