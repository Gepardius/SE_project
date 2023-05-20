from flask import Flask, render_template, g, request, redirect, session
import sqlite3


app = Flask(__name__)

app.secret_key = 'your_secret_key'

# Route handler for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve the entered username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Connect to the users database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the username and password match in the users table
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()

        # Close the database connection
        conn.close()

        if user:
            # Store the username in the session to keep the user logged in
            session['username'] = username
            return redirect('/add_income')
        else:
            # Invalid username or password, display an error message
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

# Route handler for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve the entered username, password, and confirm password from the form
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            # Passwords match, proceed with registration

            # Connect to the users database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Insert the new user into the users table
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))

            # Commit the changes and close the database connection
            conn.commit()
            conn.close()

            # Redirect the user to the login page
            return redirect('/login')
        else:
            # Passwords do not match, display an error message
            error_message = 'Passwords do not match'
            return render_template('registration.html', error_message=error_message)
    else:
        return render_template('registration.html')
    
def get_db(database):
    """Get the database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    return db

# Create the expenses table if it doesn't exist
def create_expenses_table():
    with app.app_context():
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

def create_user_table():
    with app.app_context():
        # Connect to the database (create it if it doesn't exist)
        conn = get_db('users.db')
        cursor = conn.cursor()

        # Create the 'users' table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# Route handler for adding an expense
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        # Get the expense details from the form submission
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        amount = request.form['amount']
        
        # Get the logged-in username from the session
        username = session.get('username')

        # Create the expenses table if it doesn't exist
        create_expenses_table()

        # Insert the expense into the database
        conn = get_db("expenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (username, category, description, date, amount) VALUES (?, ?, ?, ?, ?)",
            (username, category, description, date, amount)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to the index page or any other appropriate page
        return redirect('/')
    else:
        # Render the add_expense.html template with the logged-in username
        username = session.get('username')
        return render_template('add_expense.html', username=username)


# Route handler for adding an income
@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        # Get the income details from the form submission
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']
        amount = request.form['amount']
        
        # Get the logged-in username from the session
        username = session.get('username')

        # Create the expenses table if it doesn't exist
        create_expenses_table()

        # Insert the income into the database
        conn = get_db("expenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (username, category, description, date, amount) VALUES (?, ?, ?, ?, ?)",
            (username, category, description, date, amount)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to the index page or any other appropriate page
        return redirect('/')
    else:
        # Render the add_income.html template with the logged-in username
        username = session.get('username')
        return render_template('add_income.html', username=username)
    
@app.route('/view_expenses')
def view_expenses():
    conn = get_db("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_expenses.html', expenses=expenses)

@app.route('/delete_expense')
def delete_expense():
    return render_template('delete_expense.html')

if __name__ == '__main__':
    create_user_table()
    create_expenses_table()  # Create the expenses table if it doesn't exist
    app.app_context()
    app.run(debug=True)

# Close the database connection when the application context is torn down
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()