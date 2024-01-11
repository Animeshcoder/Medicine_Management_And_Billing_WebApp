from flask import Flask, request, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user
import pymysql

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'  # Set a secret key for security purposes

from twilio.rest import Client

def send_sms(to, body):
    account_sid = 'ACc852a70e075c4047c37234c7c3ab0e5d'
    auth_token = 'd031874eb41c125d06d40430ca2945d6'
    from_ = '+12134938336'

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=to,
        from_=from_,
        body=body
    )

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Set up the connection
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Animesh@006',
        database='mydatabase'
    )

    # Create a cursor
    cursor = conn.cursor()

    # Execute the SELECT statement
    cursor.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))

    # Fetch the result
    row = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    if row is not None:
        return User(row[0], row[1])

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/medicines')
def medicines():
    search_query = request.args.get('search', '')

    db_host = session.get('db_host')
    db_user = session.get('db_user')
    db_password = session.get('db_password')
    db_name = session.get('db_name')

    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cur = conn.cursor()
    if search_query:
        cur.execute("SELECT * FROM medicines WHERE name LIKE %s", (f'%{search_query}%',))
    else:
        cur.execute("SELECT * FROM medicines")
    medicines = cur.fetchall()
    medicines = [dict(zip([key[0] for key in cur.description], row)) for row in medicines]

    cur.close()
    conn.close()

    return render_template('index.html', medicines=medicines)

@app.route('/medicine/<int:medicine_id>')
def medicine(medicine_id):
    db_host = session.get('db_host')
    db_user = session.get('db_user')
    db_password = session.get('db_password')
    db_name = session.get('db_name')

    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM medicines WHERE id=%s", (medicine_id,))
    medicine = cur.fetchone()
    medicine = dict(zip([key[0] for key in cur.description], medicine))

    cur.close()
    conn.close()

    return render_template('medicine.html', medicine=medicine)

@app.route('/billing')
def billing():
    db_host = session.get('db_host')
    db_user = session.get('db_user')
    db_password = session.get('db_password')
    db_name = session.get('db_name')

    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM medicines")
    medicines = cur.fetchall()
    medicines = [dict(zip([key[0] for key in cur.description], row)) for row in medicines]

    cur.close()
    conn.close()

    return render_template('billing.html', medicines=medicines)

@app.route('/bill', methods=['POST'])
def bill():
    medicine_id = request.form['medicine_id']
    quantity = int(request.form['quantity'])
    phone_number = request.form['phone_number']

    db_host = session.get('db_host')
    db_user = session.get('db_user')
    db_password = session.get('db_password')
    db_name = session.get('db_name')

    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM medicines WHERE id=%s", (medicine_id,))
    medicine = cur.fetchone()
    medicine = dict(zip([key[0] for key in cur.description], medicine))

    total_price = float(medicine['Price_per_tablet']) * quantity
    remaining_tablets = int(medicine['Number_of_tablets']) - quantity

    # Update inventory
    cur.execute("UPDATE medicines SET Number_of_tablets=%s WHERE id=%s", (remaining_tablets, medicine_id))
    message = f"For {quantity} {medicine['Name']} tablets. You have to pay price {total_price}"
    # Send SMS to notify that medicine has been sold
    send_sms(phone_number, message)

    # Check for expired medicines
    from datetime import timedelta
    from datetime import datetime

    expiry_date = datetime.strptime(medicine['Expiry_date'], '%Y-%m-%d').date()
    today = datetime.today().date()
    if expiry_date - today == timedelta(days=10):
        message = f"{medicine['Name']} will expire in 10 days"
        # Send SMS to notify that medicine will expire in 10 days
        send_sms(phone_number, message)

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('billing'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Animesh@006',
        database='mydatabase'
    )

    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = %s AND password = %s', (username, password))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is not None:
        user_id = row[0]
        user = User(user_id, username)
        login_user(user)
        return redirect(url_for('database_form'))
    else:
        return render_template('login.html', error='Invalid credentials')

@app.route('/database_form', methods=['GET', 'POST'])
def database_form():
    if request.method == 'POST':
        db_host = request.form['db_host']
        db_user = request.form['db_user']
        db_password = request.form['db_password']
        db_name = request.form['db_name']
        phone_number = request.form['phone_number']

        session['db_host'] = db_host
        session['db_user'] = db_user
        session['db_password'] = db_password
        session['db_name'] = db_name
        session['phone_number'] = phone_number

        return redirect(url_for('medicines'))

    return render_template('database_form.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
