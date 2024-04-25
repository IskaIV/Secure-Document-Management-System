import sqlite3
from flask import Flask, render_template, request, redirect, make_response
import hashlib
import logging
from setup import start_db
from check import generate_token, check_token
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
user = ['']


@app.route('/')
def front_page():
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('SignUp.html')


@app.route('/signupvalid', methods=['POST', 'GET'])
def signupvalid():
    if request.method == "POST":
        con = sqlite3.connect('database.db')
        try:
            firstName = request.form['First']
            lastName = request.form['Last']
            WorkID = request.form['WorkID']
            password = request.form['Password']
            confirm_pass = request.form['ConfirmPassword']
            user[0] = WorkID

            hashed_password = hashlib.sha1(password.encode()).hexdigest()

            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                if (password == confirm_pass):
                    cur.execute("INSERT INTO Login (FSUID, Password, First, Last) VALUES (?,?,?,?)", (WorkID, hashed_password, firstName, lastName))
                return redirect("/")
        except:
            con.rollback()
            return render_template('Error.html')
        finally:
            con.close()


@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect('database.db')
    try:
        WorkID = request.form['WorkID']
        Password = request.form['Password']

        hashed_password = hashlib.sha256(Password.encode()).hexdigest()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE WorkID = ? AND Password = ?",
                    (WorkID, hashed_password))
        rows = cur.fetchall()
        if len(rows) == 0:
            return render_template("NoMatchingUser.html")

        token = generate_token(WorkID)
        user[0] = rows[0][0]

        response = make_response(redirect('/home'))
        response.set_cookie('AuthToken', token)

        return response
    except sqlite3.Error as e:
        logging.error(f"Database Error: {e}")
        return render_template("Error.html")
    except Exception as e:
        logging.error(f"Exception Error: {e}")
        return render_template("Error.html")
    except:
        return render_template("/")
    finally:
        con.close()
