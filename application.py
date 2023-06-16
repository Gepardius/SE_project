from flask import Flask, render_template, g, request, redirect, session
import sqlite3

application = Flask(__name__)

application.secret_key = 'your_secret_key'

# Login route
@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['username'] = username
            return redirect('/homepage')
        else:
            error_message = 'Invalid username or password'
            return render_template('index.html', error_message=error_message)
    else:
        return render_template('index.html', error_message=None)

# Logout route
@application.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Registration route
@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))

            conn.commit()
            conn.close()

            return redirect('/')
        else:
            error_message = 'Passwords do not match'
            return render_template('registration.html', error_message=error_message)
    else:
        return render_template('registration.html')

# Homepage route
@application.route('/homepage')
def homepage():
    expenses, the_table, income, the_table_income = view_last_10_transactions()

    return render_template('homepage.html', expenses=expenses, the_table=the_table, income=income, the_table_income=the_table_income)

# Helper function to get the database connection
def get_db(database):
    """Get the database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    return db

# Function to create the expenses table if it doesn't exist
def create_expenses_table():
    with application.app_context():
        conn = get_db('expenses.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                category TEXT,
                description TEXT,
                date TEXT,
                amount REAL
            )
        ''')
        conn.commit()
        cursor.close()

# Function to create the users table if it doesn't exist
def create_user_table():
    with application.app_context():
        conn = get_db('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

# Index route
@application.route('/')
def index():
    return render_template('index.html')

# Add expense route
@application.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        amount = request.form['amount']
        amount = str(amount).replace(",", ".")
        amount = float(amount) * (-1)

        username = session.get('username')

        # Create the expenses table if it doesn't exist
        create_expenses_table()

        conn = get_db("expenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (username, category, description, date, amount) VALUES (?, ?, ?, ?, ?)",
            (username, category, description, date, amount)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/add_expense')
    else:
        username = session.get('username')
        return render_template('add_expense.html', username=username)

# Add income route
@application.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        amount = request.form['amount']

        username = session.get('username')

        # Create the expenses table if it doesn't exist
        create_expenses_table()

        conn = get_db("expenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (username, category, description, date, amount) VALUES (?, ?, ?, ?, ?)",
            (username, category, description, date, amount)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/add_income')
    else:
        username = session.get('username')
        return render_template('add_income.html', username=username)

# View expenses route
@application.route('/view_expenses')
def view_expenses():
    conn = get_db("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_expenses.html', expenses=expenses)

# View username expenses route
@application.route('/my_table')
def view_username_expenses():
    conn = get_db("expenses.db")
    cursor = conn.cursor()

    username = session.get('username')
    cursor.execute("SELECT * FROM expenses WHERE username = ?", (username,))
    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('my_table.html', expenses=expenses)

# Function to view the last 10 transactions
def view_last_10_transactions():
    conn = get_db("expenses.db")
    cursor = conn.cursor()

    username = session.get('username')
    cursor.execute("SELECT * FROM expenses WHERE username = ? AND amount < 0 ORDER BY id DESC LIMIT 10", (username,))
    expenses = cursor.fetchall()

    cursor.execute("SELECT category, SUM(amount) AS TotalAmount FROM expenses WHERE username = ? and amount < 0 GROUP BY category", (username,))
    the_table = cursor.fetchall()

    cursor.execute("SELECT category, SUM(amount) AS TotalAmount FROM expenses WHERE username = ? and amount > 0 GROUP BY category", (username,))
    the_table_income = cursor.fetchall()

    cursor.execute("SELECT * FROM expenses WHERE username = ? AND amount > 0 ORDER BY id DESC LIMIT 10", (username,))
    income = cursor.fetchall()

    cursor.close()
    conn.close()

    return expenses, the_table, income, the_table_income

# Delete expense route
@application.route('/delete_expense', methods=['POST'])
def delete_expense():
    # Get the selected ID from the form data
    selected_id = request.form.get('id')

    # Connect to the expenses database
    conn = get_db("expenses.db")
    cursor = conn.cursor()

    # Execute the deletion query
    cursor.execute("DELETE FROM expenses WHERE id = ?", (selected_id,))
    conn.commit()

    # Close the database connection
    conn.close()

    # Redirect to the homepage or any other desired page
    return redirect('/my_table')

# Create the user table and expenses table
if __name__ == '__main__':
    create_user_table()
    create_expenses_table()  # Create the expenses table if it doesn't exist
    application.app_context()
    application.run(debug=True)

# Close the database connection when the application is closed
@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
