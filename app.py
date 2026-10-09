import os
import re
import sqlite3
from datetime import datetime, timezone

from flask import (Flask, render_template, request, redirect,
                   url_for, flash, g, abort)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "fans.db")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "letmein")

KINDS = ["Fan art", "Video idea", "Just saying hi"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- Database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                email      TEXT NOT NULL,
                kind       TEXT NOT NULL,
                link       TEXT,
                message    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


init_db()


# ---------- Validation ----------
def validate(form):
    errors = {}
    if not 2 <= len(form["name"]) <= 60:
        errors["name"] = "Name must be 2 to 60 characters."
    if not EMAIL_RE.match(form["email"]) or len(form["email"]) > 120:
        errors["email"] = "Please enter a valid email address."
    if form["kind"] not in KINDS:
        errors["kind"] = "Please choose one of the options."
    if form["link"] and not form["link"].startswith(("http://", "https://")):
        errors["link"] = "Links must start with http:// or https://"
    if len(form["link"]) > 300:
        errors["link"] = "That link is too long."
    if not 10 <= len(form["message"]) <= 1000:
        errors["message"] = "Message must be 10 to 1000 characters."
    return errors


# ---------- Routes ----------
SERIES = [
    {
        "title": "Animator vs. Animation",
        "meta": "2006 to 2020 · 5 main films",
        "blurb": "Where it all began: a stick figure fights back against the animator's cursor.",
        "scene": "ava",
        "thumb": "/static/img/ava.webp",  # later: "https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg"
        "url": "https://www.youtube.com/@alanbecker/search?query=Animator%20vs.%20Animation",
    },
    {
        "title": "Animation vs. Minecraft",
        "meta": "My favourite",
        "blurb": "The stick figures drop into a blocky world, and the animator has to keep up.",
        "scene": "avm",
        "thumb": "/static/img/minecraft.webp",
        "url": "https://www.youtube.com/@alanbecker/search?query=Animation%20vs.%20Minecraft",
    },
    {
        "title": "Animation vs. Education",
        "meta": "Math, physics and more",
        "blurb": "Stick figures take on school subjects, starting with Animation vs. Math.",
        "scene": "edu",
        "thumb": "/static/img/education.webp",
        "url": "https://www.youtube.com/@alanbecker/search?query=Animation%20vs.%20Math",
    },
    {
        "title": "Shorts",
        "meta": "Quick adventures",
        "blurb": "Short videos of the stick figure gang's everyday adventures.",
        "scene": "shorts",
        "thumb": None,
        "url": "https://www.youtube.com/@alanbecker/shorts",
    },
]

TIMELINE = [
    ("2006", "Posts the first Animator vs. Animation at age 17."),
    ("2007", "Animator vs. Animation II arrives, funded by Atom Films."),
    ("2011", "Animator vs. Animation III."),
    ("2014", "Animator vs. Animation IV."),
    ("2020", "Animator vs. Animation V."),
    ("2022", "Animation vs. Math kicks off the education series."),
]
IMAGES = {
    "hero": None,   
    "about": "/static/img/about.webp",
    "about_caption": "Alan Becker with the stick figure gang",
}


@app.route("/")
def home():
    return render_template("index.html", series=SERIES, timeline=TIMELINE, images=IMAGES)


@app.route("/fan-zone", methods=["GET", "POST"])
def fan_zone():
    errors, form = {}, {}

    if request.method == "POST":
        # Honeypot: real people never see this field, bots fill it in
        if request.form.get("nickname"):
            return redirect(url_for("fan_zone"))

        fields = ("name", "email", "kind", "link", "message")
        form = {k: request.form.get(k, "").strip() for k in fields}
        errors = validate(form)

        if not errors:
            db = get_db()
            db.execute(
                "INSERT INTO submissions (name, email, kind, link, message, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (form["name"], form["email"], form["kind"], form["link"] or None,
                 form["message"], datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")),
            )
            db.commit()
            flash(f"Thanks, {form['name']}! Your submission has been saved.")
            return redirect(url_for("fan_zone") + "#status")

    count = get_db().execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    status = 400 if errors else 200
    return render_template("fan_zone.html", errors=errors, form=form,
                           kinds=KINDS, count=count), status


@app.route("/admin")
def admin():
    if request.args.get("key") != ADMIN_KEY:
        abort(404)
    rows = get_db().execute(
        "SELECT * FROM submissions ORDER BY id DESC").fetchall()
    return render_template("admin.html", rows=rows)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
if __name__ == "__main__":
    app.run(debug=True)