from flask import Flask, render_template, request, session, redirect, url_for
from database import init_db
from ai_helper import generate_description, generate_skills
from flask import make_response
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
import sqlite3


app = Flask(__name__)
app.secret_key = "portfolio1234"

# ------------------------
# DATABASE CONNECTION
# ------------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------
# HOME
# ------------------------
@app.route('/')
def home():
    return render_template("index.html")

# ------------------------
# SIGNUP
# ------------------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists ❌"

        conn.close()
        return redirect(url_for('login'))

    return render_template("signup.html")

# ------------------------
# LOGIN
# ------------------------
@app.route('/login', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            # ✅ FIXED SESSION
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid Email or Password"

    return render_template('login.html', error=error)

# AI generator route
@app.route('/generate-ai', methods=['POST'])
def generate_ai():
    from flask import request, jsonify

    data = request.get_json()
    title = data.get('title')
    category = data.get('category')

    description = generate_description(title, category)
    skills = generate_skills(title)

    return jsonify({
        "description": description,
        "skills": skills
    })

# Download route
from flask import send_file

@app.route('/download')
def download():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    import sqlite3

    user_id = session['user_id']

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # GET USER DATA
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    # GET PORTFOLIOS
    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    portfolios = cursor.fetchall()

    conn.close()

    # PDF IMPORTS
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    file_path = "portfolio.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    elements = []

    # TITLE
    elements.append(Paragraph(f"<b>{user['name']}'s Portfolio</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # PROFILE SECTION
    if user['bio']:
        elements.append(Paragraph(f"<b>About:</b> {user['bio']}", styles['BodyText']))
        elements.append(Spacer(1, 10))

    if user['github']:
        elements.append(Paragraph(f"<b>GitHub:</b> {user['github']}", styles['BodyText']))

    if user['linkedin']:
        elements.append(Paragraph(f"<b>LinkedIn:</b> {user['linkedin']}", styles['BodyText']))

    elements.append(Spacer(1, 15))

    # PROJECT HEADING
    elements.append(Paragraph("<b>Projects</b>", styles['Heading1']))
    elements.append(Spacer(1, 10))

    # PROJECTS LOOP
    for p in portfolios:
        elements.append(Paragraph(f"<b>{p['title']}</b>", styles['Heading2']))
        elements.append(Spacer(1, 5))

        elements.append(Paragraph(p['description'], styles['BodyText']))
        elements.append(Spacer(1, 5))

        elements.append(Paragraph(f"<b>Skills:</b> {p['skills']}", styles['Italic']))

        if p['github']:
            elements.append(Paragraph(f"GitHub: {p['github']}", styles['BodyText']))

        if p['demo']:
            elements.append(Paragraph(f"Live Demo: {p['demo']}", styles['BodyText']))

        elements.append(Spacer(1, 15))

    # BUILD PDF
    doc.build(elements)

    return send_file(file_path, as_attachment=True)
# ------------------------
# DASHBOARD
# ------------------------
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['user_name']

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # PROFILE UPDATE
    if request.method == 'POST' and 'update_profile' in request.form:
       bio = request.form.get('bio')
       github_profile = request.form.get('github_profile')
       linkedin = request.form.get('linkedin')

       cursor.execute("""
        UPDATE users 
        SET bio=?, github=?, linkedin=? 
        WHERE id=?
     """, (bio, github_profile, linkedin, user_id))

       conn.commit()
    

   

    # ADD
    if request.method == 'POST' and 'add_portfolio' in request.form:
        title = request.form['title']
        description = request.form['description']
        skills = request.form['skills']
        github = request.form['github']
        demo = request.form['demo']
        category = request.form['category']
        # AI generation (if fields are empty)
        if not description:
           description = generate_description(title, category)
        if not skills:
           skills = generate_skills(title)

        cursor.execute("""
            INSERT INTO portfolios 
            (user_id, title, description, skills, github, demo, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title, description, skills, github, demo, category))

        conn.commit()

    # DELETE
    if request.method == 'POST' and 'delete_id' in request.form:
        cursor.execute(
            "DELETE FROM portfolios WHERE id=? AND user_id=?",
            (request.form['delete_id'], user_id)
        )
        conn.commit()

    # EDIT
    if request.method == 'POST' and 'edit_id' in request.form:
        cursor.execute("""
            UPDATE portfolios 
            SET title=?, description=?, skills=? 
            WHERE id=? AND user_id=?
        """, (
            request.form['title'],
            request.form['description'],
            request.form['skills'],
            request.form['edit_id'],
            user_id
        ))
        conn.commit()

    # FETCH
    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    portfolios = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    profile = cursor.fetchone()

    conn.close()

    return render_template(
    "dashboard.html",
    user=username,
    portfolios=portfolios,
    profile=profile   
)
    

@app.route('/portfolio/<int:user_id>')
def public_portfolio(user_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    portfolios = cursor.fetchall()

    conn.close()

    return render_template("public.html", portfolios=portfolios)

    # ------------------------
    # BUILD HTML (same style as yours)
    # ------------------------
    portfolio_html = ""

    if portfolios:
        for p in portfolios:
            portfolio_html += f"""
                <div class='card'>
                    <h3>{p['title']}</h3>
                    <p>{p['description']}</p>
                    <p><strong>Skills:</strong> {p['skills']}</p>

                    <!-- DELETE -->
                    <form method='POST'>
                        <input type='hidden' name='delete_id' value='{p['id']}'>
                        <button style='background-color:#e74c3c;'>Delete</button>
                    </form>

                    <!-- EDIT -->
                    <form method='POST'>
                        <input type='hidden' name='edit_id' value='{p['id']}'>
                        <input type='text' name='title' placeholder='New Title' required>
                        <input type='text' name='description' placeholder='New Description' required>
                        <input type='text' name='skills' placeholder='New Skills' required>
                        <button style='background-color:#f39c12;'>Edit</button>
                    </form>
                </div>
            """
    else:
        portfolio_html = "<p>No portfolio items yet 😢</p>"

    return f"""
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                max-width: 900px;
                margin: auto;
                background: #f4f6f7;
                padding: 20px;
            }}

            .card {{
                background: #3498db;
                color: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
            }}

            input, textarea {{
                display: block;
                margin: 5px 0;
                padding: 8px;
                width: 100%;
            }}

            button {{
                padding: 6px 10px;
                color: white;
                border: none;
                cursor: pointer;
            }}
        </style>
    </head>

    <body>
        <h2>Welcome, {username} 🎉</h2>
        <a href="/logout"><button style="background:red;">Logout</button></a>

        <h3>Add Portfolio</h3>
        <form method="POST">
            <input type="hidden" name="add_portfolio" value="1">
            <input type="text" name="title" placeholder="Title" required>
            <textarea name="description" placeholder="Description" required></textarea>
            <input type="text" name="skills" placeholder="Skills" required>
            <button style="background:green;">Add</button>
        </form>

        <h3>Your Work</h3>
        {portfolio_html}
    </body>
    </html>
    """

# ------------------------
# LOGOUT
# ------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)