import bible_mapping
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, escape, login_required, get_bible_verse
from datetime import datetime
import sqlite3
import logging

# Configure application
app = Flask(__name__)

# Initialise the database and migration tools after app setup
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to the SQLite database
db = SQL("sqlite:///app.db")
bible = SQL("sqlite:///kjv.db")



"""
db = sqlite3.connect("app.db", check_same_thread=False)

# Set row_factory to sqlite3.Row for dict-like access to columns
db.row_factory = sqlite3.Row
"""

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show reading history and achievements"""
    user_id = session["user_id"]

    # Fetch the user's registration date from the database
    user = db.execute("SELECT start_date FROM users WHERE id = ?", (user_id,))
    start_date = user[0]["start_date"]

    # Fetch the user's reading progress starting from the registration date
    progress = db.execute("""
        SELECT completion_date,
               chapter_1 || ' ' || start_verse_1 || '-' || end_verse_1 AS reading_1,
               chapter_2 || ' ' || start_verse_2 || '-' || end_verse_2 AS reading_2,
               chapter_3 || ' ' || start_verse_3 || '-' || end_verse_3 AS reading_3,
               chapter_4 || ' ' || start_verse_4 || '-' || end_verse_4 AS reading_4,
               completed
        FROM ReadingProgress
        WHERE user_id = ?
        ORDER BY completion_date DESC
    """, (user_id,))

    return render_template("history.html", progress=progress)


@app.route("/")
@login_required
def index():
    """Show scripture if not logged in, or reading plan if logged in"""

    # Get the current user's ID
    current_date = datetime.now().strftime("%Y-%m-%d")  # Set the current date
    return render_template("dashboard.html", current_date=current_date)  # Pass the current date




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        session["username"] = request.form.get("username")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Clear the user session
    session.clear()

    # Redirect to the login page
    return redirect("/login")


@app.route("/progress", methods=["POST","GET"])
@login_required
def progress():
    """Update reading progress"""
    user_id = session["user_id"]
    reading_id = request.form.get("reading_id")

    if not reading_id:
        return apology("invalid reading ID", 400)

    # Fetch the reading progress for the specific day and user
    reading_progress = db.execute("""
        SELECT * FROM ReadingProgress
        WHERE user_id = ? AND id = ?
    """, (user_id, reading_id))

    if reading_progress:
        reading_progress = reading_progress[0]

        # Check if all readings for the day are completed
        if all([
            reading_progress['completed_1'] == 1,
            reading_progress['completed_2'] == 1,
            reading_progress['completed_3'] == 1,
            reading_progress['completed_4'] == 1
        ]):
            # If all readings are marked as complete, increment the days_completed
            db.execute("""
                UPDATE ReadingProgress
                SET days_completed = days_completed + 1
                WHERE user_id = ? AND id = ?
            """, (user_id, reading_id))

# Review and remove /nextreadings
@app.route("/nextreadings", methods=["POST","GET"])
@login_required
def issue_readings():
    # Fetch user start_date
    user = db.execute("SELECT start_date FROM users WHERE id = ?", (user_id,))
    start_date = user[0]["start_date"]

    # Calculate the number of days since the user started
    today = datetime.now().date()
    days_since_start = (today - datetime.strptime(start_date, "%Y-%m-%d").date()).days + 1  # +1 to account for the first day

    # Fetch reading plan for the corresponding day
    reading_plan = db.execute("""
        SELECT day, month, chapter_1, start_verse_1, end_verse_1,
               chapter_2, start_verse_2, end_verse_2,
               chapter_3, start_verse_3, end_verse_3,
               chapter_4, start_verse_4, end_verse_4
        FROM McheynePlan
        WHERE day = ? AND month = ?
    """, (days_since_start, today.strftime('%B')))  # Using today's month as text

    # Check if reading plan exists for the day
    if reading_plan:
        plan = reading_plan[0]

        # Format the readings
        date_read = f"{plan['day']}-{plan['month']}"
        readings = [
            f"{plan['chapter_1']} {plan['start_verse_1']}-{plan['end_verse_1']}",
            f"{plan['chapter_2']} {plan['start_verse_2']}-{plan['end_verse_2']}",
            f"{plan['chapter_3']} {plan['start_verse_3']}-{plan['end_verse_3']}",
            f"{plan['chapter_4']} {plan['start_verse_4']}-{plan['end_verse_4']}"
        ]
    else:
        date_read = "No readings available for today."
        readings = []

    # Now fetch completed readings in descending order
    completed_readings = db.execute("""
        SELECT completion_date
        FROM ReadingProgress
        WHERE user_id = ?
        ORDER BY completion_date DESC
    """, (user_id,))
    # Fetch total chapters and completed chapters for the user
    total_chapters = db.execute("SELECT COUNT(*) FROM McheynePlan")  # Assuming McheynePlan holds total chapters
    completed_chapters = db.execute("""
        SELECT COUNT(*) FROM ReadingProgress
        WHERE user_id = ? AND completed = 1
    """, (user_id,))

    # Calculate progress percentage
    if total_chapters[0]["COUNT(*)"] > 0:
        progress_percentage = (completed_chapters[0]["COUNT(*)"] / total_chapters[0]["COUNT(*)"]) * 100
    else:
        progress_percentage = 0

    # Fetch user's completed readings
    progress = db.execute("""
        SELECT scripture_title, completion_date, completed
        FROM ReadingProgress
        WHERE user_id = ?
        ORDER BY completion_date DESC
    """, (user_id,))

    # Fetch user's start date
    start_date = db.execute("SELECT start_date FROM users WHERE id = ?", (user_id,))[0]["start_date"]

    return render_template("progress.html", progress=progress,
                           progress_percentage=progress_percentage,
                           completed_chapters=completed_chapters[0]["COUNT(*)"],
                           total_chapters=total_chapters[0]["COUNT(*)"],
                           start_date=start_date)

# Function to fetch verses from the database
def find_verses(bible, book_number, chapter):
    print(f"Book number: {book_number}, Chapter: {chapter}")  # Debugging statement
    rows = bible.execute("""
        SELECT verse, text
        FROM verses
        WHERE book_number = ? AND chapter = ?
        ORDER BY verse
    """, (book_number, chapter))
    print(f"Rows returned: {rows}")
    return rows

@app.route("/reading1", methods=["GET"])
@login_required
def reading1():
    """Get the first reading."""
    text = "Placeholder"

    book_number = 10
    chapter = 1

    # Fetch the verses using the function
    verses = find_verses(bible, book_number, chapter)

    # Debugging: Print fetched verses to verify
    print(f"Fetched verses: {verses}")

    # Iterate over rows to format the verses
    formatted_verses = []
    for row in verses:
        formatted_verses.append({
            "verse": row[0],
            "text": row[1]
        })

    # Return the rendered template with the formatted verses
    return render_template("reading1.html", verses=formatted_verses, chapter=chapter, book_number=book_number, text=text)

@app.route("/reading2")
@login_required
def reading2():
    """Display the second scripture reading"""
    user_id = session["user_id"]
    # Example: Fetch the scripture for S1 from the database or define it statically
    verses = bible.execute("""
        SELECT verse, text FROM Scriptures WHERE reading_id = 1 AND user_id = ?
    """, (user_id,))
    return render_template("reading2.html", verses=scripture_verses)

@app.route("/reading3")
@login_required
def reading3():
    """Display the third scripture reading"""
    user_id = session["user_id"]
    # Example: Fetch the scripture for S1 from the database or define it statically
    scripture_verses = [
        {"verse": 1, "text": "In the beginning God created the heaven and the earth."},
        {"verse": 2, "text": "And the earth was without form, and void; and darkness was upon the face of the deep."},
        {"verse": 3, "text": "And the Spirit of God moved upon the face of the waters."},
        {"verse": 4, "text": "And God said, Let there be light: and there was light."}
    ]
    return render_template("reading3.html", verses=scripture_verses)

@app.route("/reading4")
@login_required
def reading4():
    """Display the fourth scripture reading"""
    user_id = session["user_id"]
    # Example: Fetch the scripture for S1 from the database or define it statically
    scripture_verses = [
        {"verse": 1, "text": "In the beginning God created the heaven and the earth."},
        {"verse": 2, "text": "And the earth was without form, and void; and darkness was upon the face of the deep."},
        {"verse": 3, "text": "And the Spirit of God moved upon the face of the waters."},
        {"verse": 4, "text": "And God said, Let there be light: and there was light."}
    ]
    return render_template("reading4.html", verses=scripture_verses)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Retrieve the user's input from the name request form somewhere in HTML
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username and password are provided
        if not username or not password:
            return apology("must provide username and password", 400)

        # Check if passwords match
        if password != confirmation:
            return "Passwords do not match", 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        try:
            # Insert the new user into the users table
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed_password)
            return redirect("/login")
        except sqlite3.IntegrityError as e:
            # Handle the case where the username already exists
            print(f"Integrity error: {e}")  # Debugging statement
            return apology("username already exists", 400)
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Unexpected error: {e}")  # Debugging statement
            return apology("An unexpected error occurred", 500)

    # Render the registration form
    return render_template("register.html")

@app.route("/dashboard")
def scripture():
    """Display a specific scripture (e.g., John 1)"""

    # Fetch the scripture from the database or hardcode it (for simplicity)
    scripture_verses = [
        {"verse": 1, "text": "In the beginning was the Word, and the Word was with God, and the Word was God."},
        {"verse": 2, "text": "The same was in the beginning with God."},
        {"verse": 3, "text": "All things were made by him; and without him was not any thing made that was made."},
        {"verse": 4, "text": "In him was life; and the life was the light of men."},
        {"verse": 5, "text": "And the light shineth in darkness; and the darkness comprehended it not."},
        {"verse": 6, "text": "There was a man sent from God, whose name was John."},
        # You can add more verses here
    ]

    return render_template("dashboard.html", verses=scripture_verses)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Set or modify user's reading plan"""
    user_id = session["user_id"]
   # Fetch user details from the database
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    if request.method == "POST":
        plan_type = request.form.get("plan_type")
        translation = request.form.get("translation")
        start_date = request.form.get("start_date")

        if not plan_type or not translation or not start_date:
            return apology("must provide all settings", 400)

        # Add the new reading plan
        new_plan = ReadingProgress(
            user_id=user_id,
            plan_type=plan_type,
            translation=translation,
            start_date=datetime.strptime(start_date, "%d-%m-%Y").date()
        )
        db.session.add(new_plan)
        db.session.commit()

        flash("Reading plan set successfully!")
        return redirect("/")

    return render_template("settings.html", user=user)


